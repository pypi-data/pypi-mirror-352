# escli_tool/commands/create.py
from argparse import _SubParsersAction


def register_subcommand(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(
        "update", help="Insert a new _id according to given index name")
    parser.add_argument("--index", required=True, help="Index name to insert")
    parser.set_defaults(func=run)


def run(args):
    raise NotImplementedError("Update command is not implemented yet.")
