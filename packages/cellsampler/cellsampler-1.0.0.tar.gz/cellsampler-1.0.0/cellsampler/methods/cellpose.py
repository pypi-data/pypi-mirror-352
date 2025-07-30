from cellpose import models

from .utils import preprocess_image


@preprocess_image
def run(
    image,
    model="nuclei",
    channels=[0, 0],
    diameter=0,
    flow_threshold=0.4,
    cellprob_threshold=0.0,
    min_size=15,
    rescale=None,
    net_avg=False,
    tile=True,
    tile_overlap=0.1,
    resample=True,
    interp=True,
    progress=True,
    channel_axis=None,
    compute_masks=True,
    preprocessing=None,
    **kwargs
):
    """Run Cellpose on an image

    Parameters
    ----------
    image : str or array
        image file or array
    model : str
        'cyto' or 'nuclei'
    channels : list
        list of channels to use where 0=red, 1=green, 2=blue
    diameter : float
        if set to 0, Cellpose will estimate the cell diameter
    flow_threshold : float
        flow error threshold (default is 0.4)
    cellprob_threshold : float
        cell probability threshold (default is 0.0)
    min_size : int
        minimum number of pixels per mask (default is 15)
    rescale : float
        resize factor for each step (default is 0.2,
        set to 1.0 for no resizing)
    net_avg : bool
        flag to run cellpose averaging model
    tile : bool
        flag for breaking image into tiles for processing
    tile_overlap : float
        fraction of overlap for tiles
    resample : bool
        flag to resample image to increase/reduce size
    interp : bool
        flag for linear interpolation in resizing
    progress : bool
        flag for progress bar
    channel_axis : int
        axis for channels
    compute_masks : bool
        flag to compute masks

    Returns
    -------
    xarray.DataArray
        xarray.DataArray with masks, flows, cell probability, and cell diameter
    """

    if model == "cyto":
        model = models.Cellpose(gpu=True, model_type="cyto")
    elif model == "nuclei":
        model = models.Cellpose(gpu=True, model_type="nuclei")
    else:
        raise ValueError("model must be 'cyto' or 'nuclei'")

    if diameter == 0:
        diameter = None

    masks, flows, styles, diams = model.eval(
        image,
        diameter=diameter,
        channels=channels,
        flow_threshold=flow_threshold,
        cellprob_threshold=cellprob_threshold,
    )

    return masks
