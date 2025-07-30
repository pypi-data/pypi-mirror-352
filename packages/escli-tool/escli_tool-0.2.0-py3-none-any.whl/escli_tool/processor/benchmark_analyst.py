import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Union


from escli_tool.common import VLLM_SCHEMA
from escli_tool.handler import DataHandler
from escli_tool.data.vllm_entry import BaseDataEntry
from escli_tool.processor.processor_base import ProcessorBase
from escli_tool.registry import register_class
from escli_tool.utils import get_logger

logger = get_logger()


@register_class
class BenchmarkAnalyst:
    """
    A class to analyze the benchmark data.
    """
    CLS_BRIEF_NAME = 'analyst'

    def __init__(
        self,
        tag: str = None,
    ):
        self.schema: dict = VLLM_SCHEMA
        # Tag the schema for version control
        if tag:
            self.tag_schema(tag)
        self.data_instance: Dict[str, List[BaseDataEntry]] = {}
        self.handler = DataHandler.maybe_from_env_or_keyring()

    def tag_schema(self, tag: str):
        """
        Tag the schema with the given tag.
        """
        if tag and tag != "main":
            for key in self.schema.keys():
                self.schema[key] = (f"{self.schema[key][0]}_{tag}",
                                    self.schema[key][1])
    
    def fetch_from_es(self, size):
        self.full_data = {}
        for index_name, entry in self.schema.values():
            # Fetch data from ES
            records = self.handler.search_data_from_vllm(
                _index=index_name,
                source=True,
                size=size,
            )
            if not records or not records['hits']['hits']:
                logger.error(f"No data found in {index_name}")
                continue
            self.full_data[index_name] = records['hits']['hits']

    @staticmethod
    def extract_tp_value(s: str) -> int:
        match = re.search(r"tp(\d+)", s)
        return int(match.group(1)) if match else None

    def analysis(self):
        """
        Analysis the data, ensure the data is credible
        """

            
    def to_dict(self):
        """
        Convert the processed data to a dictionary format.
        """
        result = {}
        for index_name, entries in self.data_instance.items():
            result[index_name] = [entry.to_dict() for entry in entries]
        return result


if __name__ == '__main__':
    alalysis = BenchmarkAnalyst()
    alalysis.fetch_from_es(size=10)
    print(alalysis.full_data)
