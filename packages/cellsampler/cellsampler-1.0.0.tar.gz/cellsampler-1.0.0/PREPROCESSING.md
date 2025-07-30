# Image preprocessing

Cellsampler provides a set of image preprocessing functions that can be used to enhance the quality of the input images before segmentation. These functions are implemented in the `cellsampler/preprocessing` module and can be easily extended to add new preprocessing methods.


* Histogram equalization
* Adaptive histogram equalization
* Intensity normalization
* Hotpixel removal
* Background removal


## Histogram equalization

This just applies histogram equalization to the image. It is a simple
method that can be used to enhance the contrast of the image. It is implemented in the `cellsampler/preprocessing/equalize_hist.py` module.

## Adaptive histogram equalization

This applies adaptive histogram equalization to the image. It is a more advanced method that can be used to enhance the contrast of the image. It is implemented in the `cellsampler/preprocessing/equalize_adapthist.py` module.

```python
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
```

## Intensity normalization

This applies intensity normalization to the image. It is a method that can be used to enhance the contrast of the image. It is implemented in the `cellsampler/preprocessing/rescale_intesity.py` module.

```python   
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
```

## Background removal

This applies background removal to the image. It is a method that can be used to enhance the contrast of the image. It is implemented in the `cellsampler/preprocessing/substract_background.py` module.

```python
ef run(image, sigma=3, radius=15):
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
```

## Hotpixel removal

This applies hotpixel removal to the image using threshold over a the median value and replacing the hotpixel by the median value. It is implemented in the `cellsampler/preprocessing/remove_hotpixels.py` module.

```python
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
```