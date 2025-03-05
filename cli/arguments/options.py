import argparse


def create_base_parser(prog: str, usage: str = "", desc=None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        usage=usage,
        description=desc
    )
    add_verbosity_options(parser)
    return parser


def add_verbosity_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Enable verbose output'
    )