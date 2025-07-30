# escli_tool/commands/create.py
import os

from email.policy import default
from escli_tool.registry import get_class


def register_subcommand(subparsers):
    parser = subparsers.add_parser("add",
                                   help="Insert a new _id in the given index")
    parser.add_argument("--vllm_branch", default="v0.9.0", help="vllm version")
    parser.add_argument("--vllm_ascend_branch", default="main", help="vllm-ascend version")
    parser.add_argument("--res_dir", default=None,
                        help="Result dir which include json files")
    parser.add_argument("--processor",
                        help="Processor selected to process json files")
    parser.add_argument("--commit_id", help="Commit hash")
    parser.add_argument("--commit_title", help="Commit massage")
    parser.add_argument("--created_at",
                        help="What time current commit is submitted")
    parser.add_argument("--skip", action='store_true', default=False,
                        help="Save the data as a skipped commit")
    parser.set_defaults(func=run)


def run(args):
    """
    Insert a document loading from local dir, need to provide a processor to process the specific data.
    For example, if you want to insert performance benchmark result(which saved as json files), you need
    to provide a benchmark processor to process the json files. and the processor should process the data
    into a data format that es can accept.
    If the processor is not provided, the default processor will be used.
    """
    processor_name = args.processor
    if not processor_name:
        # Set default processor to benchmark
        processor_name = 'benchmark'
    # TODO: do not only read data from local dir, but also read dict user customized

    processor = get_class(processor_name)(
        args.commit_id,
        args.commit_title,
        args.created_at,
        args.vllm_branch,
        args.vllm_ascend_branch,
    )
    if args.skip:
        processor.send_skip()
        return
    
    if os.path.exists(args.res_dir):
        processor.send_normal(args.res_dir, )
    else:
        processor.send_error()
