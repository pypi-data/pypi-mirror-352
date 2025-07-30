"""CLI for percula."""

import argparse
from importlib import metadata
from importlib import resources
import logging
import sys

from rich.console import Console
import rich.markdown

from percula import postprocess, preprocess
from percula.util import _log_level, ColorFormatter, get_main_logger


class ShowDocs(argparse.Action):
    """Argparse action to display the software documentation."""

    def __init__(
            self, option_strings, dest=argparse.SUPPRESS,
            default=argparse.SUPPRESS, help=None):
        """Initialize the ShowDocs action."""
        super().__init__(option_strings, dest, nargs='?', help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        """Choose which documentation to show based on the option string."""
        if option_string == "--license":
            fname = "LICENSE"
        elif option_string == "--documentation":
            fname = "README.md"
        else:
            raise ValueError(f"Unknown option: {option_string}")

        readme_path = resources.files("percula").joinpath(fname)
        console = Console(width=80)
        with readme_path.open("r", encoding="utf-8") as f:
            text = f.read()
            if values == "plain":
                print(text)
            else:
                markdown = rich.markdown.Markdown(text)
                console.print(markdown)
        parser.exit()


def argument_parser():
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        'percula',
        description="Ontranger CLI: Preprocess and postprocess tools",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {metadata.version('percula')}",
        help="show the version of percula")
    parser.add_argument(
        "--license", action=ShowDocs,
        help="Show product license information.")
    parser.add_argument(
        "--documentation", action=ShowDocs,
        help="Show product documentation.")

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
    logger.info(
        "This software is distributed under the terms of the Oxford Nanopore "
        "Technologies PLC. Public License Version 1.0. The license may be reviewed "
        "by running `percula --license`.")
    logger.info(
        "For more information, please refer to the documentation with "
        "`percula --documentation`.")
    args.func(args)
