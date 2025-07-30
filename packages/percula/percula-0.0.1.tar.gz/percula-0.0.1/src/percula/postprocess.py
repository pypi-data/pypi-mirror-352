"""Postprocessing spaceranger outputs for wf-single-cell."""
import argparse
from collections import defaultdict
from contextlib import ExitStack

import pysam

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
    read_tags = defaultdict(dict)
    with pysam.AlignmentFile(
            sr_bam, "rb", check_sq=False, threads=thread_count) as processed_bam:
        for read in processed_bam.fetch(until_eof=True):
            for tag in TAGS:
                if read.has_tag(tag):
                    read_tags[read.query_name][tag] = read.get_tag(tag)
    return read_tags


def main(args):
    """Run entrypoint for the postprocess command."""
    read_tags = fetch_all_read_tags(args.sr_bam)

    with ExitStack() as context:
        raw_bam = context.enter_context(
            pysam.AlignmentFile(
                args.lr_bam, "rb", check_sq=False, threads=args.threads))
        tagged_bam = context.enter_context(
            pysam.AlignmentFile(
                args.out_bam, "wb", template=raw_bam, threads=args.threads))

        for read in raw_bam.fetch(until_eof=True):
            if read.query_name in read_tags:
                for tag, value in read_tags[read.query_name].items():
                    read.set_tag(tag, value, value_type='Z')
            tagged_bam.write(read)
