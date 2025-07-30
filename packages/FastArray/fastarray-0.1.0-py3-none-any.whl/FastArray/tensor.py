import numpy as np
import torch

def to_tensor(array: np.ndarray) -> torch.Tensor:
    """Convert a NumPy array to PyTorch tensor (float32)."""
    return torch.from_numpy(array).float()

def patchify(array: np.ndarray, patch_size: int = 256):
    """Simple patch generator from array [H, W, C]"""
    h, w, c = array.shape
    for i in range(0, h, patch_size):
        for j in range(0, w, patch_size):
            yield array[i:i+patch_size, j:j+patch_size, :]
