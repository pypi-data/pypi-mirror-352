# escli_tool/commands/create.py
from ast import main
from escli_tool.common import VLLM_SCHEMA_V1
from escli_tool.handler import DataHandler
from escli_tool.utils import get_logger

logger = get_logger()


def register_subcommand(subparsers):
    parser = subparsers.add_parser(
        "delete", help="Delete a existed _id in the given index")
    parser.add_argument("--index", help="index name")
    parser.add_argument("--id",
                        help="IDs to delete (accepts multiple IDs)",
                        nargs="+")
    parser.add_argument("--commit_id",
                        help="commit_id delete")
    parser.set_defaults(func=run)


def run(args):
    """
    Delete a document from the given index and _id list. if no _id is provided, delete the index.
    If commit_id is provided, delete the document conditional by the given commit_id. Please note that
    the commit_id is not the _id of the document, but a field in the document. and if commit_id is provided,
    all the index will be searched for the commit_id, and all the documents with the same commit_id will be deleted.
    Example:
        escli delete --index vllm_benchmark_throughput --id id1 id2 id3
        if you want to delete conditional by commit_id, please provide the commit_id:
        escli delete --commit commit_id
    """
    handler = DataHandler.maybe_from_env_or_keyring()
    if args.commit_id and args.index:
        logger.error("Cannot provide both commit_id and index.")
        return
    if args.commit_id:
        id_to_delete = []

        for index_name, _ in VLLM_SCHEMA_V1.values():
            res = handler.condition_search(index_name, {"commit_id": args.commit_id})
            if res:
                for hit in res:
                    id_to_delete.append(hit['_id'])
            logger.info(f"Deleting commit_id: {args.commit_id} from index: {index_name}")
            handler.index_name = index_name
            handler.delete_id_list_with_bulk_insert(id_to_delete)
        return
    index_name = args.index
    handler.index_name = index_name
    id_to_delete = args.id
    if not id_to_delete:
        logger.info("No IDs provided for deletion. Deleting the index.")
        handler.delete_index(args.index)
    else:
        handler.delete_id_list_with_bulk_insert(id_to_delete)
