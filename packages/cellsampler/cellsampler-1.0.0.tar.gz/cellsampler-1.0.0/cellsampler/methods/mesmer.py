import os

import numpy as np
from deepcell.applications import Mesmer

from .utils import preprocess_image


@preprocess_image
def run(image, mes_token=None, image_res_mpp=1.0, **kwargs):
    """Run StarDist on an image

    Parameters
    ----------
    image : array
        image array
    mes_token : str
        environmental token required to run Mesmer
    image_res_mpp : float
        image resolution in microns per pixel

    Returns
    -------
    array
        predicted mask
    """

    os.environ.update({"DEEPCELL_ACCESS_TOKEN": mes_token})
    mesapp = Mesmer()

    img4dnuc = np.zeros((1, np.shape(image)[0], np.shape(image)[1], 2))
    img4dnuc[0, :, :, 0] = image
    img4dnuc[0, :, :, 1] = image

    masks4d = mesapp.predict(img4dnuc, image_mpp=image_res_mpp, compartment="nuclear")
    masks = masks4d[0, :, :, 0]

    return masks
    return masks
