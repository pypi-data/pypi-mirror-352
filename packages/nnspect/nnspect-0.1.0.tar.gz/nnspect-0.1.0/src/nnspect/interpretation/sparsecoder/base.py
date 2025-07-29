from nnspect.common.config import NnspectConfig

from typing import Dict, Any


class SparseCoder:
    """SparseCoder"""

    def __init__(self, conf: NnspectConfig):
        pass

    def preprocess(self, ctx: Dict[str, Any], batched_inputs: Dict[str, Any]) -> Any:
        return ctx

    def encode(self, ctx: Dict[str, Any], features: Tensor):
        pass

    def process_interim(self, ctx: Dict[str, Any], features: Tensor) -> Tensor:
        pass

    def decode(self, ctx: Dict[str, Any], features: Tensor):
        pass

    def compute_losses(self):
        pass

    def postprocess(self):
        pass
