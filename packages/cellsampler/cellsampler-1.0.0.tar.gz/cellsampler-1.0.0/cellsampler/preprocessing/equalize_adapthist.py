import numpy as np
from skimage import exposure


def run(image, kernel_size=(50, 50), clip_limit=0.02, nbins=256):
    """Run adaptive histogram equalization on an image

    Parameters
    ----------
    image : array
        image array
    kernel_size : tuple, optional
        size of the kernel used for local histogram equalization, by default (50, 50)
    clip_limit : float, optional
        threshold for contrast limiting, by default 0.02
    nbins : int, optional
        number of bins for histogram, by default 256

    Returns
    -------
    array
        equalized image array
    """

    return exposure.equalize_adapthist(
        image, kernel_size=kernel_size, clip_limit=clip_limit, nbins=nbins
    )
