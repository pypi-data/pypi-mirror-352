# escli_tool/cli.py

import argparse

from escli_tool.commands import add, check, create, delete, login, search
from escli_tool.utils import get_logger

logger = get_logger()


def main():
    parser = argparse.ArgumentParser(prog="escli",
                                     description="Elastic CLI 工具")
    subparsers = parser.add_subparsers(dest="command")

    # register subcommand
    create.register_subcommand(subparsers)
    search.register_subcommand(subparsers)
    login.register_subcommand(subparsers)
    add.register_subcommand(subparsers)
    delete.register_subcommand(subparsers)
    check.register_subcommand(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
