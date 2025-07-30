from pathlib import Path

import xarray as xr
from cv2geojson import export_annotations, find_geocontours

# nuclear_channel_keywords = ["Ir", "193"]
nuclear_channel_keywords = ["DNA"]


class IMCDataset:
    def __init__(self, dataset_path):
        self._dataset_path = dataset_path
        self._data = xr.open_zarr(Path(dataset_path))
        self._meta = self._data.attrs["meta"][0]

    @property
    def rois(self):
        return self._meta["acquisitions"]

    def __getitem__(self, roi):
        return IMCROI(self._dataset_path, roi)


class IMCROI:
    def __init__(self, dataset_path, roi):
        self._roi = roi
        self._data = xr.open_zarr(Path(dataset_path) / roi)
        self._meta = self._data.attrs["meta"][0]
        self._roi = roi
        self._geocontours = {}

        # iterator definition
        self.start = self._data.channel[0]
        self.end = self._data.channel[-1]
        self.current = self.start

    @property
    def channels(self):
        return [
            c["metal"] + " " + c["target"] for c in self._meta["q_channels"]
        ]

    @property
    def nuclear_channel(self):
        matches = [
            [
                v.split()[-1],
                all([v.find(k) > -1 for k in nuclear_channel_keywords])
            ]
            for i, v in enumerate(self.channels)
        ]
        return [m[0] for m in matches if m[1]]

    def get_channel_index(self, channel):
        if isinstance(channel, list):
            indx = []
            nchan = len(channel)
            for nn in range(nchan):
                indx.append(
                    [
                        i
                        for i, v in enumerate(self.channels)
                        if v.find(channel[nn]) > -1
                    ][0]
                )
        else:
            indx = [
                i for i, v in enumerate(self.channels) if v.find(channel) > -1
            ][0]
        return indx

    def __getitem__(self, channel):

        if isinstance(channel, list):
            islist = True
        else:
            islist = False

        if islist is False:
            if isinstance(channel, str):
                indx = self.get_channel_index(channel)
            else:
                indx = channel
        else:
            if isinstance(channel[0], str):
                indx = self.get_channel_index(channel)
            else:
                indx = channel
        return self._data[self._roi].sel(channel=indx)

    def __iter__(self):
        self.current = self.start
        return self

    def __next__(self):
        if self.current > self.end:
            raise StopIteration
        else:
            self.current += 1
            return self._data[self._roi].sel(channel=self.current)

    @property
    def values(self):
        return self._data[self._roi].values

    def add_mask(self, mask, name, meta=None):
        self._data[f"mask_{name}"] = mask
        self._geocontours[name] = self.geocontours(name)
        # self._data[name].attrs["meta"] = self._meta
        # self._data[name].attrs["meta"][0]["name"] = name
        # self._data[name].attrs["meta"][0]["roi"] = self._roi
        # self._data[name].attrs["meta"][0]["channel"] = self.nuclear_channel
        # self._data[name].attrs["meta"][0]["channels"] = self.channels
        # self._data[name].attrs["meta"][0]["mask"] = True
        # self._data[name].attrs["meta"][0]["mask_name"] = name
        # self._data[name].attrs["meta"][0]["mask_type"] = "segmentation"
        # self._data[name].attrs["meta"][0]["mask_source"] = "cellpose"
        # self._data[name].attrs["meta"][0]["mask_source_version"] = "0.1.0"
        # self._data[name].attrs["meta"][0]["mask_source_url"] = ""

    def save(self, output_path):
        self._data.to_zarr(output_path / self._roi, mode="w")
        for name in self._geocontours:
            features = self._geocontours[name]
            output_geojson = output_path / self._roi / f"mask_{name}.geojson"
            export_annotations(features, output_geojson)

    def get_mask(self, name):
        return self._data[f"mask_{name}"]

    def geocontours(self, name):
        mask = self.get_mask(name)
        geocontours = find_geocontours(
            mask.values.astype("int32"), mode="imagej"
        )

        features = [
            contour.export_feature(color=(0, 255, 0), label="nucleus")
            for contour in geocontours
        ]
        return features
