__all__ = [
    "nn",
    "torch",
    "optim",
    "Tensor",
    "FloatTensor",
    "LongTensor",
    "HalfTensor",
    "remove_weight_norm",
    "remove_spectral_norm",
    "weight_norm",
    "spectral_norm",
    "DeviceType",
    # frequent typing
    "Optional",
    "List",
    "Dict",
    "Tuple",
    "Union",
    "TypeAlias",
    "Sequence",
    "Any",
]
import torch
from torch.nn.utils import remove_weight_norm, remove_spectral_norm
from torch.nn.utils.parametrizations import weight_norm, spectral_norm
from torch import nn, optim, Tensor, FloatTensor, LongTensor, HalfTensor
from typing import TypeAlias, Union, Optional, List, Dict, Tuple, Sequence, Any

DeviceType: TypeAlias = Union[torch.device, str]
