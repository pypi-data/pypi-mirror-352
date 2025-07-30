from scipy.ndimage import gaussian_filter
from skimage.restoration import rolling_ball


def run(image, sigma=3, radius=15):
    """Subtract background from image.

    Parameters
    ----------
    image : array
        Image array.
    sigma : float, optional
        Standard deviation for Gaussian filter, by default 3.
    radius : int, optional
        Radius for rolling ball algorithm, by default 15.
    Returns
    -------
    array
        Background-subtracted image.
    """

    image_gauss = gaussian_filter(image, sigma)
    bkg = rolling_ball(image_gauss, radius=radius)
    return image - bkg
