import numpy as np
import os
import logging

from scipy import ndimage as ndi
from skimage.segmentation import expand_labels

from .utils import preprocess_image
from .utils import preprocess_dice

from cellsampler.methods.watershed import _gauss_otsu_labeling
from cellsampler.methods.watershed import _voronoi_otsu_labeling


@preprocess_image
def run(
    image,
    labeller="voronoi",
    spot_sigma=2,
    outline_sigma=2,
    expand=2,
    threshold=1,
    **kwargs,
):
    """Run DICE-XMDB followed by the watershed on an image

    Parameters
    ----------
    image : array
        image array

    Returns
    -------
    array
        predicted mask
    """

    cur_dir = os.getcwd()
    basedir = cur_dir + "/cellsampler/methods/models/"

    dice_xmbd = preprocess_dice(image, basedir)
    prob_map = dice_xmbd.run()

    xsize = np.shape(image)[0]
    ysize = np.shape(image)[1]
    comb_prob = np.zeros((xsize, ysize))
    for xx in range(xsize):
        for yy in range(ysize):
            if np.amax(prob_map[xx, yy, :]) == prob_map[xx, yy, 0]:
                comb_prob[xx, yy] = 0.0
            else:
                comb_prob[xx, yy] = prob_map[xx, yy, 2]

    comb_prob = comb_prob.astype("float32")

    # perform watershed
    nuclei_gauss = ndi.gaussian_filter(comb_prob, sigma=1.5)
    nuclei_gauss = ndi.convolve(
        nuclei_gauss, np.asarray([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
    )

    logger = logging.getLogger(__name__)

    logger.info(f"Running labeller {labeller}")
    if labeller == "voronoi":
        labels = _voronoi_otsu_labeling(
            nuclei_gauss,
            spot_sigma=spot_sigma,
            outline_sigma=outline_sigma,
            threshold=threshold,
            **kwargs,
        )
    elif labeller == "gauss":
        labels = _gauss_otsu_labeling(
            nuclei_gauss,
            outline_sigma=outline_sigma,
            threshold=threshold, **kwargs
        )
    else:
        logger.error(f"Invalid labeller {labeller}")

    if expand > 0:
        labels = expand_labels(labels, distance=expand)

    return labels
