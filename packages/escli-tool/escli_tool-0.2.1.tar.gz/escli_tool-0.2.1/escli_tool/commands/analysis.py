# escli_tool/commands/create.py
import argparse
from ast import main
import json
from argparse import _SubParsersAction

from escli_tool.handler import DataHandler
from escli_tool.utils import get_logger
from escli_tool.common import VLLM_SCHEMA

logger = get_logger()


def register_subcommand(subparsers: _SubParsersAction):
    parser = subparsers.add_parser("analysis", help="analysis if the data is valid")
    parser.add_argument("--size",
                        required=False,
                        default=10,
                        type=int,
                        help="Size to search")
    parser.add_argument("--tag",
                        required=False,
                        help="Which version to search")
    parser.set_defaults(func=run)


def run(args):
    """Analysis the latest 10 commits, ensure the data is credible"""
    handler = DataHandler.maybe_from_env_or_keyring()
    serving_data = []
    throughput_data = []
    latency_data = []
    for index_name, _ in VLLM_SCHEMA.values():
        if args.tag and args.tag != 'main':
            index_name = f"{index_name}_{args.tag}"
        res = handler.search_data_from_vllm(index_name,
                                            source=True,
                                            size=args.size)
        if index_name == 'vllm_benchmark_serving':
            serving_data = res
        elif index_name == 'vllm_benchmark_throughput':
            throughput_data = res
        elif index_name == 'vllm_benchmark_latency':
            latency_data = res

    print(f"Serving data: {serving_data}")

    # print(f"Throughput data: {throughput_data}")
    # print(f"Latency data: {latency_data}")

