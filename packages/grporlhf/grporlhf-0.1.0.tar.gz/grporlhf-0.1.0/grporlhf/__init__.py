from importlib.metadata import version

from .trainer import GRPOTrainer
from .data_utils import build_dataset
from .utils import load_config

__all__ = ["GRPOTrainer", "build_dataset", "load_config"]
__version__ = version("grpo-rlhf")

