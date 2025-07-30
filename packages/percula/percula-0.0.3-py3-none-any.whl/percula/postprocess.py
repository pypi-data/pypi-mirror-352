"""Postprocessing spaceranger outputs for wf-single-cell."""
import argparse
from collections import defaultdict
from contextlib import ExitStack
from timeit import default_timer as now

import pysam

from percula.util import get_named_logger


TAGS = ['CR', 'CB', 'UR', 'UB']


def argument_parser():
    """Create argument parser for the postprocess command."""
    parser = argparse.ArgumentParser(
        'postprocess',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        'sr_bam', type=str,
        help='Path to the SpaceRanger output possorted_genome_bam.bam file.')
    parser.add_argument(
        'lr_bam', type=str,
        help='Path to the raw long-reads BAM file')
    parser.add_argument(
        "out_bam", type=str,
        help='Path to the output BAM file with added tags.')
    parser.add_argument(
        '--threads', type=int, default=3,
        help='Number of threads to use for processing BAM files.')
    return parser


def fetch_all_read_tags(sr_bam, thread_count=4):
    """Fetch all read tags from the processed SpaceRanger .bam."""
    logger = get_named_logger('TagFetcher')
    read_tags = defaultdict(dict)
    t0 = now()
    logger.info(f'Starting to fetch read tags from {sr_bam}.')
    with pysam.AlignmentFile(
            sr_bam, "rb", check_sq=False, threads=thread_count) as processed_bam:
        for n_reads, read in enumerate(processed_bam.fetch(until_eof=True), 1):
            for tag in TAGS:
                if read.has_tag(tag):
                    read_tags[read.query_name][tag] = read.get_tag(tag)
                else:
                    read_tags[read.query_name][tag] = None
            if n_reads % 1000000 == 0:
                elapsed = now() - t0
                rps = n_reads / elapsed
                logger.info(
                    f'Processed {n_reads} reads ({rps / 1000:.1f}k reads/s)')
    logger.info(
        f'Fetched tags for {len(read_tags)} reads from {sr_bam}.')
    return read_tags


def main(args):
    """Run entrypoint for the postprocess command."""
    logger = get_named_logger('BamTagger')
    logger.warning(
        "If you intend to process data with wf-single, do not run this "
        "program. Instead provide the Spacer Ranger BAM to wf-single-cell "
        "directly.")
    read_tags = fetch_all_read_tags(args.sr_bam)

    t0 = now()
    logger.info(f'Starting to process {args.lr_bam}.')
    logger.info(
        f'Output will be written to {args.out_bam}.')
    n_reads = 0
    missing = 0
    with ExitStack() as context:
        raw_bam = context.enter_context(
            pysam.AlignmentFile(
                args.lr_bam, "rb", check_sq=False, threads=args.threads))
        tagged_bam = context.enter_context(
            pysam.AlignmentFile(
                args.out_bam, "wb", template=raw_bam, threads=args.threads))

        for n_reads, read in enumerate(raw_bam.fetch(until_eof=True), 1):
            if read.query_name in read_tags:
                for tag, value in read_tags[read.query_name].items():
                    read.set_tag(tag, value, value_type='Z')
            else:
                missing += 1
                logger.debug(
                    f"Read {read.query_name} not found in tags, skipping.")
            tagged_bam.write(read)
            if n_reads % 1000000 == 0:
                elapsed = now() - t0
                rps = n_reads / elapsed
                logger.info(
                    f'Processed {n_reads} reads ({rps / 1000:.1f}k reads/s)')
    if missing > 0:
        logger.warning(
            f"{missing} reads from long-read BAM were not found in the "
            "SpaceRanger tags.")
    logger.info(f"Written {n_reads} reads to {args.out_bam}.")
    logger.info("Finished processing.")
