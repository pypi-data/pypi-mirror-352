"""CLI for percula."""

import argparse
from importlib.metadata import version
import logging
import sys

from percula import postprocess, preprocess
from percula.util import _log_level, ColorFormatter, get_main_logger


def argument_parser():
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        'percula',
        description="Ontranger CLI: Preprocess and postprocess tools",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {version('percula')}",
        help="show the version of percula")

    subparsers = parser.add_subparsers(
        title='subcommands', description='valid commands',
        help='additional help', dest='command')
    subparsers.required = True

    p = subparsers.add_parser(
        "preprocess", parents=[_log_level(), preprocess.argument_parser()])
    p.set_defaults(func=preprocess.main)

    p = subparsers.add_parser(
        "postprocess", parents=[_log_level(), postprocess.argument_parser()])
    p.set_defaults(func=postprocess.main)

    return parser


def main():
    """Run main entry point for the CLI."""
    parser = argument_parser()
    args = parser.parse_args()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter(
        fmt='[%(asctime)s - %(name)s] %(message)s',
        datefmt='%H:%M:%S'))

    logger = get_main_logger("percula")
    logger.setLevel(args.log_level)
    logger.handlers = []  # clear existing handlers
    logger.addHandler(handler)

    logger.info("Welcome")
    args.func(args)
