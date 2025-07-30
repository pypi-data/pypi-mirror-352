import numpy as np
from skimage import exposure


def run(image, p1=2, p2=98):
    """Rescale intensity of an image

    Parameters
    ----------
    image : array
        image array
    p1 : int, optional
        lower percentile for rescaling, by default 2
    p2 : int, optional
        upper percentile for rescaling, by default 98

    Returns
    -------
    array
        rescaled image array
    """
    p2, p98 = np.percentile(image, (p1, p2))
    return exposure.rescale_intensity(image, in_range=(p2, p98))
