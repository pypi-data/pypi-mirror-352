from abc import ABC

from escli_tool.handler import DataHandler


class ProcessorBase(ABC):

    def __init__(self, commit_id: str, commit_title, created_at: str):
        self.commit_id = commit_id
        self.commit_title = commit_title
        self.created_at = created_at
        self.handler = DataHandler.maybe_from_env_or_keyring()

    def fetch_from_es(self, index_name: str, size: int, source: bool = True):
        full_data = self.handler.search_data_from_vllm(index_name)
        return full_data