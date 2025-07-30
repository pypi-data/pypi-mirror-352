# escli_tool/commands/create.py
from argparse import _SubParsersAction

from escli_tool.handler import DataHandler
from escli_tool.utils import get_logger

logger = get_logger()


def register_subcommand(subparsers: _SubParsersAction):
    parser = subparsers.add_parser("check", help="Check for an existed _id")
    parser.add_argument("commit_file",
                        nargs="?",
                        default=None,
                        help="Text file to filter the commit id")
    parser.add_argument("--index",
                        default='vllm_benchmark_throughput_v1',
                        help="The index name to search")
    parser.add_argument("--source",
                        action="store_true",
                        default=True,
                        help="Whether to expand details")
    parser.add_argument("--size",
                        required=False,
                        default=1000,
                        type=int,
                        help="Size to search")
    parser.set_defaults(func=run)


def run(args):
    """Filter the commit id from the given file"""
    handler = DataHandler.maybe_from_env_or_keyring()
    index_name = args.index
    records = handler.search_data_from_vllm(index_name,
                                            source=args.source,
                                            size=args.size)
    recorded_commits = set()
    cur_commits = set()
    for hit in records['hits']['hits']:
        _source = hit.get('_source')
        if _source:
            commit_id = _source.get('commit_id')
            if commit_id:
                recorded_commits.add(commit_id)
            else:
                # For backward compatibility, if commit_id is not found, use the _id
                recorded_commits.add(hit['_id'])
    if not args.commit_file:
        logger.error("No commit file provided. Exiting.")
        return
    lines = []
    with open(args.commit_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
                cur_commits.add(line.split()[0])
    remaining_commits = cur_commits - recorded_commits
    filtered_lines = [
        line for line in lines if line.split()[0] in remaining_commits
    ]
    logger.info(
        f"Filtered {len(filtered_lines)} commits from {len(cur_commits)} commits"
    )
    with open(args.commit_file, 'w') as f:
        for i, line in enumerate(filtered_lines):
            print('-' * 100)
            print(line)
            if i == len(filtered_lines) - 1:
                f.write(line)
                print("-" * 100)
            else:
                f.write(line + '\n')
