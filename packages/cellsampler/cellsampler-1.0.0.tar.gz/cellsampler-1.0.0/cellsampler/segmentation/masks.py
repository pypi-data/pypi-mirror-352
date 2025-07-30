import logging
import numpy as np
from pathlib import Path
import os

from cellsampler import methods

from .uber import UBM
from .imcdataset import IMCDataset

logger = logging.getLogger(__name__)


def run_mask(config):

    path = Path(config["input"]) / config["dataset"]
    dataset = IMCDataset(path)

    for roi in dataset.rois:
        imc_roi = dataset[roi]
        nuc_chan = imc_roi.nuclear_channel
        logging.info(f"Processing ROI {roi}")
        logging.info(f"Nuclear channel: {nuc_chan}")
        logging.info(
            f"Channel index: {imc_roi.get_channel_index(nuc_chan)}"
        )

        all_masks = []
        logging.info("Checking for any trained methods")
        main_dir = os.path.dirname(os.path.dirname(__file__))
        mo_path = "/methods/models/"
        mo_dir = main_dir + mo_path + config["sd_trained"]["model"]
        if "sd_trained" in config["runs"] and os.path.isdir(mo_dir) is False:
            logging.error(
                f"Running sd_trained requires a model within {mo_dir}"
            )
            quit()

        for run_name in config["runs"]:
            logging.info(f"Performing run: {run_name}")
            method_name = config[run_name]["method"]
            label_name = config[run_name]["label"]
            method = getattr(methods, method_name)
            mask = method.run(imc_roi, **config[run_name])
            imc_roi.add_mask(mask.array, label_name)
            all_masks.append(mask)

        lenm = len(config["runs"])
        all_array = np.zeros(
            (lenm, np.shape(all_masks[0])[0], np.shape(all_masks[0])[1])
        )
        for ll in range(lenm):
            all_array[ll, :, :] = all_masks[ll].array.data

        for crit in config["merit"]:
            logging.info(f" Forming Ubermask with criteria: {crit}")
            ubmask = UBM(all_array)
            umask, labels = ubmask.form_um(merit=crit, nsize=config["nsize"])
            imc_roi.add_mask(umask, crit)
            imc_roi.add_mask(labels, crit + "_labels")

        imc_roi.save(Path(config["output"]) / config["dataset"])

    logging.info("Done")
