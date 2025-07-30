import logging
from pathlib import Path
import dask
from dask.distributed import Client

from ..segmentation.imcdataset import IMCDataset
from .statistics import cellextractor

logger = logging.getLogger(__name__)


@dask.delayed
def save_ch_cats(thisr, msk, config, roi, lname):

    df = cellextractor(thisr, msk)
    df["channel"] = thisr.channel.values
    output_catalogue_dir = (
        Path(config["output"]) / config["dataset"] / roi / f"mask_{lname}" / "catalogue"
    )
    output_catalogue_dir.mkdir(parents=True, exist_ok=True)
    output_catalogue_parquet = output_catalogue_dir / f"{thisr.channel.values}.parquet"
    df.to_parquet(output_catalogue_parquet)

    logging.info(f"Saved catalogue {output_catalogue_parquet}")

    return None


def run_catalogue(config):

    path = Path(config["output"]) / config["dataset"]
    dataset = IMCDataset(path)
    client = Client(threads_per_worker=1, n_workers=1)
    pp = client.cluster.scale(25)
    logging.info(f"{pp}")

    for roi in dataset.rois:
        imc_roi = dataset[roi]
        logging.info(f"Processing ROI {roi}")

        for run_name in config["runs"]:
            logging.info(f"Performing run: {run_name}")
            label_name = config[run_name]["label"]
            mask = imc_roi.get_mask(label_name)
            no_ch = len(imc_roi.channels)
            a = []
            for intv in range(no_ch):
                thechan = imc_roi[intv]
                a.append(save_ch_cats(thechan, mask, config, roi, label_name))
            dask.compute(a)

        for criteria in config["merit"]:
            logging.info(f"Performing uber run: {criteria}")
            mask = imc_roi.get_mask(criteria)
            no_ch = len(imc_roi.channels)
            b = []
            for intv in range(no_ch):
                thechan = imc_roi[intv]
                b.append(save_ch_cats(thechan, mask, config, roi, criteria))
            dask.compute(b)
