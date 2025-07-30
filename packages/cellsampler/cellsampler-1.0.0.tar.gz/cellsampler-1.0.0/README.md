# Cellsampler - Robust consensus image segmentation</p>
<img src="https://gitlab.developers.cam.ac.uk/astronomy/camcead/imaxt/public-code/cellsampler/-/raw/main/cellsampler.jpeg?ref_type=heads" width="250" title="cellsmapler" alt="cellsampler" align="right" vspace="5" />

Cellsampler is a Python package for generating masks and catalogues of cells in images using multiple segmentation methods and using consensus in order to select the best segmentation for each image region. It has been designed to work with IMC (Imaging Mass Cytometry) datasets stored in Zarr format but can be adapted for other imaging modalities. The package is built on top of the Cellpose, Stardist, and Watershed segmentation methods, providing a unified interface to apply these methods to your datasets.

It supports by default following segmentation methods:
- [Cellpose](https://github.com/MouseLand/cellpose)
- Stardist
- Watershed
- Mesmer

The interface to these methods is described in the [Segmentation](SEGMENTATION.md) document. The package also provides a set of image preprocessing methods that can be used to enhance the quality of the input images before segmentation. These methods are described in the [Preprocessing](PREPROCESSING.md) document.

See [Extending Cellsampler](EXTENDING.md) for more information on how to add your own image preprocessing and segmentation methods.


## Installation

To install the software use `pip` a below
```
pip install cellsampler
```

The above does not install the segmentation methods from other repositories. To do this you can use:

```
pip install cellsampler[cellpose,stardist]
```

or install the segmentation software independently.

For development of for extending the code clone the repository and install in editable mode:

```
git clone https://gitlab.developers.cam.ac.uk/astronomy/camcead/imaxt/public-code/cellsampler.git
cd cellsampler
pip install -e .
``` 


## Configuration
The package uses a YAML configuration file to specify the parameters for each segmentation method. The configuration file allows you to customize the parameters for each method, including the model type, threshold, and other settings.

For more details please refer to the default configuration file `config.yaml` in the root directory of the repository. 

## Usage


### IMC Datasets

To generate masks and catalogues alter the yaml file as appropriate and run from the command line: 

```
cellsampler -c config.yaml 
```

The explanation of the config.yaml file is given inside the file. 

The input dataset is a IMC dataset in Zarr format. The output is a copy of the input IMC dataset with added masks for each method in Zarr format and a catalogue of the cells in the dataset.

Example output Zarr with masks for each method:

```
<xarray.Dataset> Size: 2GB
Dimensions:        (channel: 53, y: 3054, x: 3551)
Coordinates:
  * channel        (channel) int64 424B 0 1 2 3 4 5 6 7 ... 46 47 48 49 50 51 52
  * x              (x) int64 28kB 0 1 2 3 4 5 ... 3545 3546 3547 3548 3549 3550
  * y              (y) int64 24kB 0 1 2 3 4 5 ... 3048 3049 3050 3051 3052 3053
Data variables:
    Q001           (channel, y, x) float32 2GB dask.array<chunksize=(4, 382, 444), meta=np.ndarray>
    mask_cellpose  (y, x) uint16 22MB dask.array<chunksize=(382, 888), meta=np.ndarray>
    mask_stardist  (y, x) int32 43MB dask.array<chunksize=(382, 444), meta=np.ndarray>
```


### Generic Datasets
To generate masks and catalogues for generic datasets in other formats, you can use the `cellsampler` module directly. The module provides a unified interface to apply the segmentation methods to your datasets.

Examples of how to use the package with different datasets are provided in the `notebooks` directory. The examples include:

- Using Cellsampler with multi-channel TIFF files
- ...


## Roadmap

- [ ] [Add support for OME-Zarr format](https://gitlab.developers.cam.ac.uk/astronomy/camcead/imaxt/public-code/cellsampler/-/issues/1)
- [ ] [Include support for multiple channel TIFF files](https://gitlab.developers.cam.ac.uk/astronomy/camcead/imaxt/public-code/cellsampler/-/issues/2)
- [ ] [Add support for additional preprocessing methods](https://gitlab.developers.cam.ac.uk/astronomy/camcead/imaxt/public-code/cellsampler/-/issues/3)
- [ ] Add visualization tools for the generated masks and catalogues


## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements


## Citation


## Changelog

For a list of changes to the package, please refer to the [CHANGELOG](CHANGELOG.md) file.




