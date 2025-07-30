# Image segmentation

Cellsampler provides a set of image segmentation methods that can be used to segment cells in images. These methods are implemented in the `cellsampler/methods` module and can be easily extended to add new segmentation methods.

Currently the package supports the following segmentation methods:
- Cellpose
- Stardist
- Mesmer
- Watershed

For further details on each segmentation method, please refer to the original methods' documentation.

## Cellpose

Cellpose is a deep learning-based segmentation method that can be used to segment cells in images. It is implemented in the `cellsampler/methods/cellpose.py` module.

```python
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
```

## Stardist

Stardist is a deep learning-based segmentation method that can be used to segment cells in images. It is implemented in the `cellsampler/methods/stardist.py` module.

```python
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
```


## Mesmer

Mesmer is a deep learning-based segmentation method that can be used to segment cells in images. It is implemented in the `cellsampler/methods/mesmer.py` module.

```python
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
```

## Watershed

Watershed is a classical image segmentation method that can be used to segment cells in images. It is implemented in the `cellsampler/methods/watershed.py` module.

```python
def run(
    image,
    labeller="voronoi",
    spot_sigma=2,
    outline_sigma=2,
    expand=2,
    threshold=1,
    **kwargs,
):
    """Run the watershed segmentation algorithm on an image.
    Parameters
    ----------
    image : array
        Image array.
    labeller : str, optional
        Labeller to use, "voronoi" or "gauss", by default "voronoi".
    spot_sigma : float, optional
        Sigma for spot detection, by default 2.
    outline_sigma : float, optional
        Sigma for outline detection, by default 2.
    expand : int, optional
        Expand labels by this distance, by default 2.
    threshold : float, optional
        Threshold for the labeller, by default 1.

    Returns
    -------
    array
        Segmented image.
    """
```

