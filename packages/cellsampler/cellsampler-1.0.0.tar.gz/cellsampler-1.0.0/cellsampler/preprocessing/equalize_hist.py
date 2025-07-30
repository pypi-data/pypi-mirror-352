from skimage import exposure


def run(image):
    """Run histogram equalization on an image

    Parameters
    ----------
    image : array
        image array

    Returns
    -------
    array
        equalized image array
    """
    return exposure.equalize_hist(image)
