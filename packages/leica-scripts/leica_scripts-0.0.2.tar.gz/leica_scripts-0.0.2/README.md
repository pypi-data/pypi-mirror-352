# Leica_ROI_finder
Automatic ROI finder for Leica Stellaris 8
- Automatic segmentation using cellpose 3
- ROI filtering using intensity, size and circularity
- Exports ROIs to Leica .rgn files, can be imported into LAS X navigator

![](./assets/images/usage.gif)

## Installation and usage
Leica ROI finder is available on PyPi and can be installed as follows:
```shell
pip install leica-scripts
```

Activate the GUI using:
```shell
python -m leica_scripts
```

# Workflow
Load LIF image into ROI finder:

![](./assets/images/image_loaded.png)

Perform segmentation using cellpose, filter ROIs using intensity, size and circularity:

![](./assets/images/segmentation.png)

Ron Scripts:

![](./assets/images/regions_loaded.png)

Perform imaging on all regions:

![](./assets/images/experiment.png)