import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Union


from escli_tool.common import VLLM_SCHEMA_V1
from escli_tool.data.vllm_entry import BaseDataEntry
from escli_tool.data.vllm_entry import BenchmarkStatus
from escli_tool.processor.processor_base import ProcessorBase
from escli_tool.registry import register_class
from escli_tool.utils import get_logger

logger = get_logger()


@register_class
class BenchmarkProcessor(ProcessorBase):
    CLS_BRIEF_NAME = 'benchmark'

    def __init__(
        self,
        commit_id: str,
        commit_title: str,
        created_at: str = None,
        vllm_branch: str = "v0.9.0",
        vllm_ascend_branch: str = "main",
    ):
        super().__init__(commit_id, commit_title, created_at)
        self.schema: dict = VLLM_SCHEMA_V1
        self.device = "Ascend910B3"
        self.vllm_branch = vllm_branch
        self.vllm_ascend_branch = vllm_ascend_branch
        self.data_instance: Dict[str, List[BaseDataEntry]] = {}

    @staticmethod
    def _read_from_json(folder_path: Union[str, Path]):
        res_map = {}
        for file_name in os.listdir(folder_path):
            if file_name.endswith("json"):
                file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    res_map[Path(file_name).stem] = json_data
            except json.JSONDecodeError as e:
                logger.error(
                    f"can not read from json: {file_name}, error: {e}")
                sys.exit(1)
        return res_map

    def tag_schema(self, tag: str):
        """
        Tag the schema with the given tag.
        """
        if tag != "main":
            for key in self.schema.keys():
                self.schema[key] = (f"{self.schema[key][0]}_{tag}",
                                    self.schema[key][1])

    @staticmethod
    def extract_tp_value(s: str) -> int:
        match = re.search(r"tp(\d+)", s)
        return int(match.group(1)) if match else None

    def process(self, folder_path: str):
        """
        Process the json files in the given folder path and return a dictionary
        containing the processed data.
        """
        commit_id = self.commit_id
        commit_title = self.commit_title
        json_data = self._read_from_json(folder_path)
        # Instanceiate the data class dynamically from the schema
        for test_name, benchmark_results in json_data.items():
            test_prefix = str.split(test_name, "_")[0]
            tp = self.extract_tp_value(test_name)
            benchmark_tuple = self.schema.get(test_prefix)
            if not benchmark_tuple:
                logger.warning(f"Unknown test prefix: {test_prefix}")
                continue
            index_name, benchmark_data_class = benchmark_tuple
            if not self.data_instance.get(index_name):
                self.data_instance[index_name] = []
            self.data_instance[index_name].append(
                benchmark_data_class(
                    commit_id=commit_id,
                    commit_title=commit_title,
                    test_name=test_name,
                    tp=tp,
                    created_at=self.created_at,
                    device=self.device,
                    vllm_branch=self.vllm_branch,
                    vllm_ascend_branch=self.vllm_ascend_branch,
                    extra_features=None,  # type: ignore
                    **{
                        key: value
                        for key, value in benchmark_results.items()
                        if key in benchmark_data_class.__annotations__.keys()
                    },
                ))
            
    def to_dict(self):
        """
        Convert the processed data to a dictionary format.
        """
        result = {}
        for index_name, entries in self.data_instance.items():
            result[index_name] = [entry.to_dict() for entry in entries]
        return result

    def send_normal(self, folder_path: str):
        """
        Send the processed data to Elasticsearch.
        """
        self.process(folder_path)
        for index_name, entries in self.data_instance.items():
            for entry in entries:
                _id = self.makeup_id(entry)
                self.handler.index_name = index_name
                if hasattr(entry, 'request_rate'):
                    print(entry.to_dict())
                self.handler.add_single_data(id=_id, data=entry.to_dict())
    
    def send_error(self, error_message: str):
        """
        Send error message to Elasticsearch.
        """
        for _, data_entry in self.schema:
            index_name, _ = data_entry
            err_id_to_save = self.commit_id[:8] + "_error"
            self.handler.index_name = index_name
            self.handler.add_single_data(id=err_id_to_save, data={
                "status": BenchmarkStatus.ERROR.value,
                "commit_id": self.commit_id,
                "commit_title": self.commit_title,
                "created_at": self.created_at,
                })

    
    def send_skip(self):
        """
        Send skip message to Elasticsearch.
        """
        for _, data_entry in self.schema.items():
            index_name, _ = data_entry
            skip_id_to_save = self.commit_id[:8] + "_skip"
            self.handler.index_name = index_name
            self.handler.add_single_data(id=skip_id_to_save, data={
                "status": BenchmarkStatus.SKIP.value,
                "commit_id": self.commit_id,
                "commit_title": self.commit_title,
                "created_at": self.created_at,
                })

    @staticmethod
    def makeup_id(entry: BaseDataEntry) -> str:
        """
        Make up the unique _id interactive with es.
        """
        if not entry.commit_id:
            raise ValueError("commit_id is required to generate _id")
        if not entry.test_name:
            raise ValueError("test_name is required to generate _id")
        if not entry.tp:
            raise ValueError("tp is required to generate _id")

        required_fields = ['commit_id', 'model_name']
        for field in required_fields:
            if not getattr(entry, field):
                raise ValueError(f"{field} is required to generate _id")
        _id_parts = [
            entry.commit_id[:8],
            str(entry.request_rate)
            if hasattr(entry, 'request_rate') else None,
            entry.model_name,
        ]
        _id = '_'.join(filter(None, _id_parts))
        return _id
