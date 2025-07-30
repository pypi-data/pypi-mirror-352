import xarray as xr

from cellsampler.plotting import plt_to_png, png_to_html, show_image


class LabellerData:
    def __init__(self, labels):
        self._labels = labels

    @property
    def labels(self):
        return self._labels

    @property
    def shape(self):
        return self._labels.shape

    @property
    def dtype(self):
        return self._labels.dtype

    def min(self):
        return self._labels.min()

    def max(self):
        return self._labels.max()

    @property
    def array(self):
        return xr.DataArray(
            self.labels,
            dims=("y", "x"),
            coords={"y": range(self.shape[0]), "x": range(self.shape[1])},
        )

    def _repr_html_(self):
        show_image(self._labels, labels=True, continue_drawing=True)
        image = png_to_html(plt_to_png())
        all = [
            "<table>",
            "<tr>",
            "<td>",
            image,
            "</td>",
            '<td style="text-align: center; vertical-align: top;">',
            "<table>",
            "<tr><td>shape</td><td>"
            + str(self.shape).replace(" ", "&nbsp;")
            + "</td></tr>",
            "<tr><td>dtype</td><td>" + str(self.dtype) + "</td></tr>",
            "<tr><td>min</td><td>" + str(self.min()) + "</td></tr>",
            "<tr><td>max</td><td>" + str(self.max()) + "</td></tr>",
            "</table>",
            "</td>",
            "</tr>",
            "</table>",
        ]
        return "\n".join(all)
