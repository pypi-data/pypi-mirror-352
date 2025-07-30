import ctypes
from pathlib import Path

import numpy as np
from scipy import LowLevelCallable, ndimage

pwd = Path(__file__).parent.resolve()

clib = ctypes.cdll.LoadLibrary(
    pwd.glob("nice_filters*.so").__next__().__str__()
)

clib.mad_filter.restype = ctypes.c_int

clib.mad_filter.argtypes = (
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_long,
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_void_p,
)

mad_filter_llc = LowLevelCallable(clib.mad_filter)


def run(image, threshold=10, npass=3, filter_size=5):
    """
    Remove hot pixels from an image using a median filter and a modified
    local contrast filter.

    Parameters
    ----------
    image : array
        Image array.
    threshold : int, optional
        Threshold for hot pixel detection, by default 10.
    npass : int, optional
        Number of passes for filtering, by default 3.
    filter_size : int, optional
        Size of the filter, by default 5.

    Returns
    -------
    array
        Filtered image.
    """

    img = image.copy()
    for i in range(npass):
        img_b = ndimage.median_filter(img, size=[filter_size, filter_size])
        img_r = 1.48 * ndimage.generic_filter(
            img, mad_filter_llc, [filter_size, filter_size]
        )
        difference = np.abs(img - img_b)
        filtered = np.where(difference > threshold * img_r, img_b, img)
        img = filtered
    return img
