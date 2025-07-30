"""Process long-reads data to pseudo-short read fastqs compatible to run SpaceRanger."""
import argparse
from collections import Counter, namedtuple
from contextlib import ExitStack
from functools import partial
import itertools
import json
from multiprocessing import Manager, Process
from pathlib import Path
import sys
from timeit import default_timer as now

import edlib
from isal import igzip
import msgpack
import pysam

from percula.util import get_named_logger, SafeJoinableQueue


REVCOMP = str.maketrans("ACGTacgt", "TGCAtgca")


def reverse_complement(seq):
    """Rev comp sequence."""
    return seq[::-1].translate(REVCOMP)


# Visium HD 3' Adapter Sequences
adapters = {
    'adapter1_f': 'CTACACGACGCTCTTCCGATCT',
    'adapter2_f': 'ATGTACTCTGCGTTGATACCACTGCTT',
}
adapters['adapter1_r'] = reverse_complement(adapters['adapter1_f'])
adapters['adapter2_r'] = reverse_complement(adapters['adapter2_f'])

config_map = {
    "adapter2_r-adapter2_f": 'double_adapter2',
    "adapter2_f-adapter2_r": 'double_adapter2',
    "adapter1_r-adapter1_f": 'double_adapter1',
    "adapter1_f-adapter1_r": 'double_adapter1',
    "adapter2_f": 'single_adapter2',
    "adapter2_r": 'single_adapter2',
    "adapter1_f": 'single_adapter1',
    "adapter1_r": 'single_adapter1',
    "*": "no_adapters"}

# Required entries for configs.json output
possible_configs = [
    "single_adapter1",
    "single_adapter2",
    "double_adapter1",
    "double_adapter2",
    "no_adapters",
    "full_length",
    "subreads",
    "stranded",
    "plus",
    "minus",
    "other"
]

valid_adapter_pairs = {
    ('adapter1_f', 'adapter2_f'): 'f',
    ('adapter2_r', 'adapter1_r'): 'r'
}

Read = namedtuple(
    'Read',
    ['query_name', 'query_sequence', 'query_qualities_str', 'tags'])

BAD_TAGS = set("AS CC CG CP H1 H2 HI H0 IH MC MD MQ NM SA TS".split())


def argument_parser():
    """Create argument parser for the preprocess command."""
    parser = argparse.ArgumentParser(
        "preprocess",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        "output", type=str,
        help="Output directory for the processed fastq files and bam."
    )
    parser.add_argument(
        "bam", nargs='+',
        help="Path(s) to the input long-read BAM files or directories."
    )
    parser.add_argument(
        "--threads", default=4, type=int,
        help="Worker threads to use for processing reads."
    )
    parser.add_argument(
        "--chunk_size", default=500000, type=int,
        help="Chunksize for multiprocessing."
    )
    parser.add_argument(
        "--max_reads", default=None, type=int,
        help="Maximum number of reads to process, otherwise all reads."
    )
    parser.add_argument(
        "--sample_name", default='SAMPLE',
        help="Sample name for output file prefix."
    )
    parser.add_argument(
        "--r1_size", default=43, type=int,
        help="Number of bases after the adapter to include in R1 fastq file."
    )
    parser.add_argument(
        "--r2_size", default=200, type=int,
        help="Number of bases after the adapter to include in R2 fastq file."
    )
    parser.add_argument(
        "--min_id", default=0.8, type=float,
        help="Minimum identity to call an adapter."
    )
    return parser


def get_reads(inputs, max_reads=None):
    """Read the input long-reads data in chunks."""
    logger = get_named_logger('Reader')
    if max_reads is None:
        logger.info("No maximum reads limit set, processing all reads")
        max_reads = float('inf')
    else:
        logger.info(f"Limiting to {max_reads} reads")
    total_reads = 0
    warn_count = 0
    for fname in inputs:
        logger.info(f"Reading from {fname}")
        with pysam.AlignmentFile(fname, check_sq=False, threads=4) as fh:
            for record in fh.fetch(until_eof=True):
                # st tag should be in all records whether from MinKNOW or dorado
                if warn_count < 10 and not record.has_tag('st'):
                    warn_count += 1
                    logger.warning(
                        f"Record {record.query_name} appears to be missing "
                        "meta data. This may lead to unexpected results in "
                        f"downstream analysis.")
                    if warn_count == 10:
                        logger.warning(
                            "Further warnings about missing meta data "
                            "will be suppressed.")
                tags = record.get_tags(with_value_type=True)
                tags = [
                    (tag, value, tcode) for tag, value, tcode, in tags
                    if tag not in BAD_TAGS]
                tags = msgpack.packb(tags, use_bin_type=True)  # pickle is slow
                yield (
                    record.query_name,
                    record.query_sequence,
                    record.query_qualities_str,
                    tags)
                total_reads += 1
                if total_reads >= max_reads:
                    logger.info(f"Reached maximum reads limit: {max_reads}")
                    return


def collect_bam_files(paths):
    """Expand input paths into a list of valid BAM files."""
    logger = get_named_logger('BAMCollector')
    bam_files = []
    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and path.suffix.lower() == ".bam":
            bam_files.append(path)
        elif path.is_dir():
            # TODO: rglob is recursive, do we only want glob?
            bam_files.extend(p for p in path.rglob("*.bam") if p.is_file())
        else:
            logger.error(
                f"Input path is not a BAM file or directory: {path}")
    return bam_files


def read_chunks(bams, input_queue, chunk_size=50000, max_reads=None):
    """Read the input long-reads data in chunks."""
    logger = get_named_logger('Reader')
    if len(bams) == 1 and bams[0] == '-':
        logger.info("Reading BAM data from standard input.")
    else:
        bams = collect_bam_files(bams)

    total_reads = 0
    t0 = now()
    reads = get_reads(bams, max_reads=max_reads)
    while chunk := list(itertools.islice(reads, chunk_size)):
        total_reads += len(chunk)
        input_queue.put(chunk)
        t1 = now()
        rps = total_reads // (t1 - t0)
        logger.debug(
            f"Read {total_reads / 1e6:.1f}M reads "
            f"({rps / 1000:.1f} kreads / s, queue: {input_queue.qsize()})")
    logger.info(f"Read {total_reads} reads from {len(bams)} BAM file(s)")


def get_subreads(read, r1_size, r2_size, min_id, min_length=200, trim=44):
    """Split long-reads into R1/R2 sub-reads based on presence of adapter pairs."""
    pairs = []
    parents = []
    hit_summary = []
    config_summary = Counter()
    edlib_hits = []
    # the minimum length of a read should at least be the length
    # of a a plausible protein-coding transcript (~180nt)
    min_length = max(min_length, r1_size, r2_size)

    read = Read(*read)
    for adapter, adapter_seq in adapters.items():
        max_ed = int(len(adapter_seq) * (1 - min_id))
        result = edlib.align(
            adapter_seq, read.query_sequence,
            mode="HW",
            task="locations",
            k=max_ed)

        if result['editDistance'] != -1 and result['editDistance'] <= max_ed:
            for loc in result['locations']:
                edlib_hits.append([adapter, loc])

    # sort the hits by start position
    edlib_hits.sort(key=lambda x: x[1][0])

    n_valid_segments = 0
    for i in range(len(edlib_hits) - 1):
        # get adapters that would be first in a valid pair, depending on strand
        if not edlib_hits[i][0] in ['adapter1_f', 'adapter2_r']:
            continue
        a1 = edlib_hits[i]
        a2 = edlib_hits[i + 1]
        subread_orientation = valid_adapter_pairs.get((a1[0], a2[0]))
        if subread_orientation:
            a1_end = a1[1][1] + 1
            a2_start = a2[1][0]

            # filter seqs that are too short
            length = a2_start - a1_end
            if length < min_length:
                config_summary['too_short'] += 1
                continue

            subread_id = f"{read.query_name}_{n_valid_segments}"
            subread_seq = read.query_sequence[a1_end:a2_start]
            subread_qual = read.query_qualities_str[a1_end:a2_start]
            config_summary['stranded'] += 1

            n_valid_segments += 1
            if subread_orientation == 'f':
                config_summary['plus'] += 1
                # For Visium HD 3' reads, those with 'r' adapters will be in the mRNA
                # antisense orientation. If so we reverse complement to + strand
                subread_seq = reverse_complement(subread_seq)
                subread_qual = subread_qual[::-1]
            else:
                config_summary['minus'] += 1

            hit_summary.append(
                (f"{subread_id}\t{subread_orientation}\t"
                 f"{a1[0]}\t{a1_end}\t{a2[0]}\t{a2_start}\n"))

            # Read structure at the point. (YBC: Y-barcode, XBC: X-barcode)
            # Note that the R1 adapter and TSO have been trimmed
            # 5' TSO / cDNA-NB{30}TBB-G-YBC{13,14}-G-XBC{13,14}-G-UMI{9,10,11} / R1 5'

            # Take the first part of the subread before the Read1 adapter containing
            # the barcode and UMI. Reverse complement as the barcodes are encoded
            # on the antisense strand.
            r1 = "@{} 1:N:0:0\n{}\n+\n{}\n".format(
                subread_id,
                reverse_complement(subread_seq[-r1_size:]),
                subread_qual[-r1_size:][::-1])
            # Get a cDNA section from the 5' of the subread just after the TSO
            r2 = "@{} 4:N:0:0\n{}\n+\n{}\n".format(
                subread_id,
                subread_seq[:r2_size],
                subread_qual[:r2_size])
            # Get the full length subread, trimming the barcode and UMI using the max
            # sizes of the barcodes and UMI.
            # 44 bases is the length of the largest barcode UMI combination plus G
            # sapcers and Vs before the polyA.
            if trim is not None:
                subread_seq = subread_seq[:-trim]
                subread_qual = subread_qual[:-trim]
            parents.append((
                subread_id, subread_seq, subread_qual, read.tags))
            pairs.append((r1, r2))

    # if the read has at least one valid subread, class it as full length
    config_summary['subreads'] = n_valid_segments
    if config_summary['subreads'] > 0:
        config_summary['full_length'] += 1
    else:
        # 'other' represents complex read adapter configurations
        read_config = "-".join([a[0] for a in edlib_hits])
        if len(edlib_hits) == 0:
            read_config = 'no_adapters'
        else:
            read_config = config_map.get(read_config, 'other')
        config_summary[read_config] += 1

    return pairs, parents, config_summary, hit_summary


def process_chunk(
        input_queue, output_queue, bamout_queue,
        r1_size, r2_size, min_id, wid=None):
    """Process a set of reads."""
    logger = get_named_logger(f'Aligner{wid}')
    logger.info("Initializing.")
    while True:
        reads, parents, configs = [], [], []
        chunk = input_queue.get()

        if chunk is None:
            input_queue.task_done()
            break

        t0 = now()
        for read in chunk:
            pairs, ps, c, _ = get_subreads(read, r1_size, r2_size, min_id)
            reads.extend(pairs)
            parents.extend(ps)
            configs.extend(c)
        input_queue.task_done()
        t1 = now()
        rps = len(chunk) // (t1 - t0)
        logger.debug(
            f"Processed {len(chunk)} reads "
            f"({rps / 1000:.1f} kreads / s, queue: {input_queue.qsize()})")
        configs = Counter(configs)
        output_queue.put((reads, configs))
        bamout_queue.put(parents)
    logger.info("Finished processing.")


def writer_thread(output_dir, output_queue, output_configs, sample_name):
    """Write FASTQ entries from queue to files."""
    logger = get_named_logger('FASTWriter')
    r1_fname = output_dir / f"{sample_name}_S1_L001_R1_001.fastq.gz"
    r2_fname = output_dir / f"{sample_name}_S1_L001_R2_001.fastq.gz"

    written = 0
    all_configs = Counter()
    t0 = None  # measured below from when we get the first result
    with ExitStack() as stack:
        r1_fh = stack.enter_context(igzip.open(r1_fname, "wt", compresslevel=1))
        r2_fh = stack.enter_context(igzip.open(r2_fname, "wt", compresslevel=1))
        while True:
            chunk = output_queue.get()
            if t0 is None:
                t0 = now()
            if chunk is None:
                output_queue.task_done()
                break
            read_pairs, configs = chunk
            all_configs.update(configs)

            # use of igzip buys us 4x (4.7s->1.1), string join on top another 5x (>0.2s)
            # (string join with vanilla gzip not worth anything)
            # this allows us to scale to reading being bottleneck with 16 edlib workers
            # (only 7-8 workers are occupied at steady state)
            r1_buff = []
            r2_buff = []
            for r1, r2 in read_pairs:
                written += 1
                r1_buff.append(r1)
                r2_buff.append(r2)
            r1 = "".join(r1_buff)
            r2 = "".join(r2_buff)
            r1_fh.write(r1)
            r2_fh.write(r2)

            output_queue.task_done()
            t1 = now()
            rps = written // (t1 - t0)
            logger.info(
                f"Written {written / 1e6:.1f}M read pairs "
                f"({rps / 1000:.1f} kreads / s, queue: {output_queue.qsize()})")
    # update global config counter, we're the only writer
    for k, v in all_configs.items():
        output_configs[k] = v
    t1 = now()
    rps = written // (t1 - t0)
    logger.info(
        f"Written {written/1e6:0.1f}M read pairs ({rps / 1000:.1f} kreads / s) "
        f"to {r1_fname} and {r1_fname}")


def bam_writer_thread(output_dir, output_queue, sample_name):
    """Write FASTQ entries from queue to files."""
    logger = get_named_logger('BAMWriter')
    bam_fname = output_dir / f"{sample_name}_S1_L001.bam"
    header = pysam.AlignmentHeader.from_dict({
        "HD": {"VN": "1.6", "SO": "unknown"},
        "SQ": []  # required even for unmapped BAMs
    })

    written = 0
    t0 = None  # measured below from when we get the first result
    with ExitStack() as stack:
        bam_fh = stack.enter_context(
            pysam.AlignmentFile(bam_fname, "wb", header=header, threads=4))
        while True:
            chunk = output_queue.get()
            if t0 is None:
                t0 = now()
            if chunk is None:
                output_queue.task_done()
                break

            for parent in chunk:
                written += 1
                rec = pysam.AlignedSegment(header=header)
                rec.query_name = parent[0]
                rec.query_sequence = parent[1]
                rec.query_qualities_str = parent[2]
                if parent[3] is not None:
                    tags = msgpack.unpackb(parent[3], raw=False)
                    rec.set_tags(tags)
                bam_fh.write(rec)

            output_queue.task_done()
            t1 = now()
            rps = written // (t1 - t0)
            logger.debug(
                f"Written {written / 1e6:.1f}M bam records "
                f"({rps / 1000:.1f} kreads / s, queue: {output_queue.qsize()})")
    t1 = now()
    rps = written // (t1 - t0)
    logger.info(
        f"Written {written/1e6:0.1f}M bam records ({rps / 1000:.1f} kreads / s) "
        f"to {bam_fname}.")


def main(args):
    """Run entrypoint for the preprocess command."""
    logger = get_named_logger('preprocess')
    try:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logger.error(
            f"Output directory '{args.output}' already exists. "
            "Please remove it or choose a different name.")
        sys.exit(1)

    t0 = now()

    # could be removed, just for easier testing
    QueueType = SafeJoinableQueue
    WorkerType = Process

    with Manager() as manager:
        config_counter = manager.dict()  # to retrieve from writer Process
        # Initialize counter with possible config types
        for cfg_type in possible_configs:
            config_counter[cfg_type] = 0
        input_queue = QueueType(maxsize=args.threads * 2)
        output_queue = QueueType(maxsize=args.threads * 4)
        bamout_queue = QueueType(maxsize=args.threads * 4)

        # first stage of pipeline is reading inputs, however this is done below
        # in main thread to allow for use case of reading stdin as input

        # start worker threads to process chunks of reads
        worker = partial(
            process_chunk, input_queue=input_queue,
            output_queue=output_queue, bamout_queue=bamout_queue,
            r1_size=args.r1_size, r2_size=args.r2_size, min_id=args.min_id)
        workers = []
        for wid in range(args.threads):
            work = WorkerType(target=worker, kwargs={"wid": wid})
            work.start()
            workers.append(work)

        # start a thread to write fastq.gz files asynchronously
        writer = WorkerType(
            target=writer_thread,
            args=(output_dir, output_queue, config_counter, args.sample_name))
        writer.start()
        # ...and one for BAM
        bam_writer = WorkerType(
            target=bam_writer_thread,
            args=(output_dir, bamout_queue, args.sample_name))
        bam_writer.start()

        # read the data, this will block until all reads are processed
        logger.info("Starting to read input data.")
        read_chunks(
            args.bam, input_queue,
            chunk_size=args.chunk_size, max_reads=args.max_reads)

        # wait for things in order
        for _ in workers:
            input_queue.put(None)
        for work in workers:
            work.join()
        logger.info("All workers finished processing. Waiting for fastq completion.")
        output_queue.put(None)
        bamout_queue.put(None)
        writer.join()
        logger.info("Waiting for BAM writer to finish.")
        bam_writer.join()
        logger.info("Finished processing all data. Writing summary counts.")

        # write summary counts
        counters = Counter(dict(config_counter))
        config_fname = output_dir / 'configs.json'
        with open(config_fname, 'w') as f:
            json.dump(counters, f, indent=4)
        logger.info(f"Wrote configuration summary to {config_fname}")
    t1 = now()
    logger.info(f"Finished processing in {t1 - t0:.0f} seconds")
    logger.info(f"Output files may be found in {output_dir.resolve()}")
