import os
from typing import TYPE_CHECKING, Any, Callable

from escli_tool.data.vllm_entry import (LatencyDataEntry, ServingDataEntry,
                                        ThroughputDataEntry)

VLLM_SCHEMA = {
    "serving": ("vllm_benchmark_serving", ServingDataEntry),
    "latency": ("vllm_benchmark_latency", LatencyDataEntry),
    "throughput": ("vllm_benchmark_throughput", ThroughputDataEntry),
}

VLLM_SCHEMA_V1 = {
    "serving": ("vllm_benchmark_serving_v1", ServingDataEntry),
    "latency": ("vllm_benchmark_latency_v1", LatencyDataEntry),
    "throughput": ("vllm_benchmark_throughput_v1", ThroughputDataEntry),
}

VLLM_SCHEMA_TEST = {
    'serving': ('vllm_benchmark_serving_test1', ServingDataEntry),
    "latency": ("vllm_benchmark_latency_test1", LatencyDataEntry),
    "throughput": ("vllm_benchmark_throughput_test1", ThroughputDataEntry),
}

if TYPE_CHECKING:
    ES_CACHE_ROOT: str = os.path.expanduser("~/.cache/escli")
    ES_CONFIG_ROOT: str = os.path.expanduser("~/.config/escli")


def get_default_config_root():
    return os.getenv(
        "ES_CONFIG_HOME",
        os.path.join(os.path.expanduser("~"), ".config"),
    )


environment_variables: dict[str, Callable[[], Any]] = {
    "ES_CONFIG_ROOT":
    lambda: os.path.expanduser(
        os.getenv("ES_CONFIG_ROOT",
                  os.path.join(get_default_config_root(), "escli")))
}


def __getattr__(name: str):
    # lazy evaluation of environment variables
    if name in environment_variables:
        return environment_variables[name]()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return list(environment_variables.keys())


def is_set(name: str):
    """Check if an environment variable is explicitly set."""
    if name in environment_variables:
        return name in os.environ
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
