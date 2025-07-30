from escli_tool.handler import DataHandler
from escli_tool.utils import get_logger, save_credentials

logger = get_logger()


def register_subcommand(subparsers):
    parser = subparsers.add_parser("login", help="login to Elastic serve")
    parser.add_argument(
        "--domain",
        required=True,
        help="Elasticsearch domain(eg: http://localhost:9200)",
    )
    parser.add_argument("--token", required=True, help="Authorization Token")
    parser.set_defaults(func=run)


def run(args):
    try:
        DataHandler(args.domain, args.token)
        save_credentials(args.domain, args.token)
        logger.info("✅ login successful")
    except ConnectionError as e:
        logger.error(f"❌ login error: {e}")
