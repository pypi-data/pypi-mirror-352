import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from numpy.random import MT19937, RandomState, SeedSequence

rs = RandomState(MT19937(SeedSequence(3)))
lut = rs.rand(65537, 3)
lut[0, :] = 0
# these are the first four colours from matplotlib's default
lut[1] = [0.12156862745098039, 0.4666666666666667, 0.7058823529411765]
lut[2] = [1.0, 0.4980392156862745, 0.054901960784313725]
lut[3] = [0.17254901960784313, 0.6274509803921569, 0.17254901960784313]
lut[4] = [0.8392156862745098, 0.15294117647058825, 0.1568627450980392]
colormap = ListedColormap(lut)


def plt_to_png():
    """PNG representation of the image object for IPython.
    Returns
    -------
    In memory binary stream containing a PNG matplotlib image.
    """
    from io import BytesIO

    import matplotlib.pyplot as plt

    with BytesIO() as file_obj:
        plt.savefig(file_obj, format="png")
        plt.close()  # supress plot output
        file_obj.seek(0)
        png = file_obj.read()
    return png


def png_to_html(png):
    import base64

    url = "data:image/png;base64," + base64.b64encode(png).decode("utf-8")
    return f'<img src="{url}"></img>'


def show_image(
    im,
    title: str = None,
    clip_pct=0.05,
    cmap=None,
    interpolation="nearest",
    labels=False,
    continue_drawing=False,
):
    args = {}
    if clip_pct and im.dtype != bool:
        args["vmin"] = np.percentile(im.ravel(), clip_pct)
        args["vmax"] = np.percentile(im.ravel(), 100 - clip_pct)
    if labels:
        args["cmap"] = colormap
    if cmap is not None:
        args["cmap"] = cmap
    args["interpolation"] = interpolation
    plt.imshow(im, **args)
    plt.axis(False)
    if title:
        plt.title(title)
    if not continue_drawing:
        plt.show()
