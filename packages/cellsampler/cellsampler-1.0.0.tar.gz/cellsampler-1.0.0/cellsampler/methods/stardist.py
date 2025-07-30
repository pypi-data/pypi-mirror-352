import os

from stardist.models import StarDist2D

from .utils import preprocess_image


@preprocess_image
def run(image, model="2D_versatile_fluo", threshold=0.5, **kwargs):
    """Run StarDist on an image

    Parameters
    ----------
    image : array
        image array
    model : str
        path to the StarDist model
    threshold : float
        threshold for the predicted mask

    Returns
    -------
    array
        predicted mask
    """

    if model == "2D_versatile_fluo":
        model = StarDist2D.from_pretrained(model)
        labels, _ = model.predict_instances(image)
    else:
        cur_dir = os.path.dirname(__file__)
        model = StarDist2D(None, name=model, basedir=cur_dir + "/models/")
        labels, _ = model.predict_instances(image)

    return labels
    return labels
