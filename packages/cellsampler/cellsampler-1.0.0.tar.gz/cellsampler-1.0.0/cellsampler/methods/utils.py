import logging
import math
import os
import shutil

import dask.array as da
import numpy as np
import pandas as pd
from skimage import exposure, io
from skimage.feature import canny
from skimage.filters import gaussian
from skimage.util import img_as_ubyte, img_as_uint

from cellsampler import preprocessing
from cellsampler.segmentation.labellerdata import LabellerData

from .cnn import predict

logger = logging.getLogger(__name__)


def preprocess_image(func):
    def wrapper(image, *args, **kwargs):

        try:
            # TODO: check if config has nuclear channel, otherwise use default
            image = image[image.nuclear_channel].values
            if len(np.shape(image)) == 3:
                logger.info("Averaging channels together")
                image = np.mean(image, axis=0)
        except AttributeError:
            pass

        if "preprocessing" not in kwargs:
            preproc = []
        else:
            preproc = kwargs["preprocessing"]
            logger.info(f"Running preprocessing: {preproc}")
        for p in preproc:
            if p in kwargs:
                image = getattr(preprocessing, p).run(image, **kwargs[p])
            else:
                image = getattr(preprocessing, p).run(image)
        labels = func(image, *args, **kwargs)
        return LabellerData(labels)

    return wrapper


class preprocess_dice:
    def __init__(self, image, basedir):
        self._image = image
        self._basedir = basedir

        self._nc_path = basedir + "Nuc_cytos/"
        self._pm_path = basedir + "Prob_maps/"
        os.makedirs(basedir + "Nuc_cytos/")
        os.makedirs(basedir + "Prob_maps/")

        fakedata = {
            "Tile_index": "999",
            "LocZ_start": [0],
            "LocZ_fin": [0],
            "LocY_start": [0],
            "LocY_fin": [0],
            "LocX_start": [0],
            "LocX_fin": [0],
        }
        TL_df = pd.DataFrame.from_dict(fakedata)
        TL_name = basedir + "tileloc"
        self._tl = TL_name
        TL_df.to_csv(
            TL_name,
            columns=[
                "Tile_index",
                "LocZ_start",
                "LocZ_start",
                "LocY_start",
                "LocY_fin",
                "LocX_start",
                "LocX_fin",
            ],
            index=False,
        )

    def apply_contrast_stretching(self, img):

        p2, p98 = np.percentile(img, (0.1, 99.9))
        img_rescale = exposure.rescale_intensity(img, in_range=(p2, p98))
        img_rescale = img_rescale.astype(np.uint16)

        return img_rescale

    def get_synthetic_cyto_from_nuclear(self, im_nuc_16bit):
        """
        Read a gray-scale/16bit nuclear channel image from imc and
        synthetically create an image resembling of membrane channel.

        input
            - im_nuc_16bit[np.arr]: 16bit array of the nuclear image.

        output
            - im_synthetic[np.arr]: 16bit array (same size as input image).
        """

        im_nuc_16bit = self.apply_contrast_stretching(im_nuc_16bit)
        im_nuc_8bit = img_as_ubyte(im_nuc_16bit)
        im_nuc_8bit = gaussian(im_nuc_8bit, sigma=0.2)
        im_nuc_8bit = canny(im_nuc_8bit)
        im_nuc_8bit = gaussian(im_nuc_8bit, sigma=1.0)

        im_synthetic = img_as_uint(im_nuc_8bit)

        return im_synthetic

    def get_full_probmap(self, gsize, olap, x1, x2, y1, y2):

        prob_map_list = [f for f in os.listdir(self._pm_path) if f.endswith(".tiff")]
        tloc_data = pd.read_csv(self._tl, converters={"Tile_index": str})

        maxY = np.amax(tloc_data["LocY_fin"])
        maxX = np.amax(tloc_data["LocX_fin"])
        conv = (gsize - 2 * olap) / gsize

        full = np.zeros((int(maxY * conv), int(maxX * conv), 3))

        # loop through all prob-maps (tiles) and perform segmentation
        for ii in range(len(prob_map_list)):

            prob_map_imageName = prob_map_list[ii]

            tile_index_str_p = prob_map_imageName.split("_")[1]
            tile_index_str_p = tile_index_str_p.split(".")[0]

            img = io.imread(self._pm_path + prob_map_imageName)

            all_inds = tloc_data["Tile_index"]
            this_tile_p = np.where(all_inds == tile_index_str_p)[0]

            y_st = int(tloc_data["LocY_start"][this_tile_p].values[0] * conv)
            y_end = int(tloc_data["LocY_fin"][this_tile_p].values[0] * conv)
            x_st = int(tloc_data["LocX_start"][this_tile_p].values[0] * conv)
            x_end = int(tloc_data["LocX_fin"][this_tile_p].values[0] * conv)

            full[y_st:y_end, x_st:x_end, :] = img[olap:-olap, olap:-olap, :]

        return full[x1:x2, y1:y2, :]

    def save_perform(self, tile_nc, block_info=None):
        """
        function that saves out the Nuc_cyto tile,
        then performs the CNN on that tile and saves the results of the CNN
        """
        istr = (
            str(block_info[0]["chunk-location"][0])
            + str(block_info[0]["chunk-location"][1])
            + str(block_info[0]["chunk-location"][2])
        )

        loc_info = block_info[0]["array-location"]
        newdata = {
            "Tile_index": istr,
            "LocZ_start": [loc_info[0][0]],
            "LocZ_fin": [loc_info[0][1]],
            "LocY_start": [loc_info[1][0]],
            "LocY_fin": [loc_info[1][1]],
            "LocX_start": [loc_info[2][0]],
            "LocX_fin": [loc_info[2][1]],
        }
        df = pd.DataFrame.from_dict(newdata)
        df.to_csv(self._tl, mode="a", header=False, index=False)

        # Save masked 'Nuc+Cyto' roi
        io.imsave(
            self._nc_path + "NucCyto_" + istr + ".tiff", tile_nc, check_contrast=False
        )

        pname = "02-15-20-14_threshold-99.7_withAugnoise-0.5_model_80.pth"
        weight_path = self._basedir + pname
        INPUT_CNN_ARGS = {
            "path_in": self._nc_path,
            "path_out": self._pm_path,
            "model_name": "BRCA1",
            "weight": weight_path,
            "cuda": "0,1,2,3",
            "th": 99.7,
            "n_input_channel": 3,
            "file_ext_current": "NucCyto_" + istr + ".tiff",
            "file_ext_new": "ProbMap_" + istr + ".tiff",
        }

        # Run the CNN model
        predict(INPUT_CNN_ARGS)

        return tile_nc

    def pad_image(self, gsize, olap):

        span = gsize - 2 * olap
        X_SIZE = np.shape(self._image)[0]
        Y_SIZE = np.shape(self._image)[1]

        totalypad = int((math.ceil(Y_SIZE / span) * span) - Y_SIZE)
        totalxpad = int((math.ceil(X_SIZE / span) * span) - X_SIZE)
        right_padding = int(np.floor(totalxpad / 2.0))
        left_padding = int(np.ceil(totalxpad / 2.0))
        top_padding = int(np.floor(totalypad / 2.0))
        bottom_padding = int(np.ceil(totalypad / 2.0))

        newX = X_SIZE + totalxpad
        newY = Y_SIZE + totalypad

        padded = np.zeros((newX, newY))
        cutx1 = right_padding
        cutx2 = newX - left_padding
        cuty1 = bottom_padding
        cuty2 = newY - top_padding
        padded[cutx1:cutx2, cuty1:cuty2] = self._image

        return padded, cutx1, cutx2, cuty1, cuty2

    def run(self):

        good_size = 512
        overlap = 50
        theim, cx1, cx2, cy1, cy2 = self.pad_image(good_size, overlap)

        NUC_CYTO_list = list()
        copyim = theim.copy()
        copyim = ((copyim / copyim.max()) * 255).astype(np.uint16)
        CYTO_ARRAY_SYNTHETIC = self.get_synthetic_cyto_from_nuclear(copyim)

        NUC_CYTO_list.append(copyim)
        NUC_CYTO_list.append(CYTO_ARRAY_SYNTHETIC)
        NUC_CYTO = np.array(NUC_CYTO_list)

        chunk_nuccyto = da.from_array(
            NUC_CYTO,
            chunks=(2, good_size - 2 * overlap, good_size - 2 * overlap),
        )

        chunk_nuccyto.map_overlap(
            self.save_perform,
            depth={0: 0, 1: overlap, 2: overlap},
            boundary={0: 0, 1: 0, 2: 0},
            dtype=NUC_CYTO.dtype,
            trim=False,
            allow_rechunk=False,
        ).compute()

        comb_prob = self.get_full_probmap(good_size, overlap, cx1, cx2, cy1, cy2)

        # Housekeeping
        shutil.rmtree(self._nc_path)
        shutil.rmtree(self._pm_path)
        os.remove(self._tl)

        return comb_prob
