import numpy as np

def ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """Compute NDVI from NIR and Red bands."""
    ndvi_val = (nir - red) / (nir + red + 1e-10)
    return np.clip(ndvi_val, -1, 1)

def ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Compute NDWI from Green and NIR bands."""
    ndwi_val = (green - nir) / (green + nir + 1e-10)
    return np.clip(ndwi_val, -1, 1)
