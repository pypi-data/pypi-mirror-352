# escli_tool/commands/create.py
import json
from argparse import _SubParsersAction

from escli_tool.handler import DataHandler
from escli_tool.utils import get_logger

logger = get_logger()


def register_subcommand(subparsers: _SubParsersAction):
    parser = subparsers.add_parser("search", help="search for an existed _id")
    parser.add_argument("--index",
                        required=True,
                        help="The index name to search")
    parser.add_argument("--source",
                        action="store_true",
                        help="Whether to expand details")
    parser.add_argument("--commit_id",
                        required=False,
                        help="Optional commit hash to search")

    parser.add_argument("--size",
                        required=False,
                        default=1000,
                        type=int,
                        help="Size to search")
    parser.set_defaults(func=run)


def run(args):
    """Search for an existed _id in the given index"""
    handler = DataHandler.maybe_from_env_or_keyring()
    index_name = args.index
    res = handler.search_data_from_vllm(index_name,
                                        source=args.source,
                                        size=args.size)
    print_formatted_results(res)
    return res


def print_formatted_results(res):
    """Format and print the search results"""
    if not res or 'hits' not in res or 'hits' not in res['hits']:
        print("No results found.")
        return
    print(f"Search took: {res['took']}ms")
    print(f"Total hits: {res['hits']['total']['value']}")
    print("-" * 50)

    print("================= Search Results =================")
    res_len = len(res['hits']['hits'])
    print(f"Number of hits: {res_len}")
    print("==================================================")
    for hit in res['hits']['hits']:
        print(f"Index: {hit['_index']}")
        print(f"ID: {hit['_id']}")
        if '_source' in hit:
            print("Source:")
            print(json.dumps(hit['_source'], indent=4))
        print("-" * 50)
