from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, Union
import json


@dataclass
class BaseDataEntry:
    commit_id: str
    commit_title: str
    test_name: str
    vllm_branch: str
    vllm_ascend_branch: str
    device: str
    tp: int
    created_at: Union[str, None]
    extra_features: Union[dict, None]

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

        if not self.extra_features:
            self.extra_features = {}

    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)
