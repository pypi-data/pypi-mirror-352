import gc
import torch
from torch import mps, cuda


def clear_memory():
    gc.collect()
    if cuda.is_available():
        cuda.empty_cache()
    if torch.backends.mps.is_available():
        mps.empty_cache()


def get_device(use_cpu=False):
    return torch.device(
        "cuda:0"
        if torch.cuda.is_available()
        else ("mps" if torch.backends.mps.is_available() else "cpu")
    )
