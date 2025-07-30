import logging as builtin_logging
import sys
from argparse import ArgumentParser, FileType, Namespace
from typing import List

import yaml

from .catalogue import run_catalogue
from .logging import setup_logging
from .segmentation.masks import run_mask

__version__ = "1.0.0"
__author__ = "Melis Irfan and Eduardo Gonzalez Solares"
__email__ = ""

logger = builtin_logging.getLogger(__name__)


def parse_args(input: List[str]) -> Namespace:
    """Parse command line arguments

    Parameters
    ----------
    input : list
        List of command line arguments


    Returns
    -------
    Namespace
        Parsed command line arguments

    """
    parser = ArgumentParser(description="CellSampler")

    parser.add_argument("--config", "-c", type=FileType("r"), help="Configuration file")

    args = parser.parse_args(input)

    return args


def _initialize_output(config):
    """Initialize the output directory and copy the input dataset to the output directory

    Parameters
    ----------
    config : dict
        Configuration dictionary containing the input and output paths

    """
    from pathlib import Path

    import xarray as xr

    path = Path(config["input"]) / config["dataset"]
    ds_input = xr.open_zarr(path)
    ds_output = xr.Dataset()
    ds_output.attrs["meta"] = ds_input.attrs["meta"]
    try:
        ds_output.to_zarr(Path(config["output"]) / config["dataset"])
    except Exception:
        pass


def main():
    """Main entry point for the cellsampler command line"""

    setup_logging(log_level=builtin_logging.DEBUG)

    logger.info("Welcome to CellSampler!")
    logger.info(f"Version: {__version__}")

    args = parse_args(sys.argv[1:])
    config = yaml.safe_load(args.config.read())
    logger.info(f"Arguments: {config}")

    _initialize_output(config)

    logger.info("Making Masks")
    run_mask(config)

    logger.info("Making Catalogues")
    run_catalogue(config)
