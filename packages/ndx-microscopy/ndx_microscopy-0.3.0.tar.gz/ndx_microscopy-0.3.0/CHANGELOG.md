# v0.3.0 (Jun 3, 2025)
## Bug Fixes

## Deprecations and Changes
- Removed `ExcitationLightPath` and `EmissionLightPath` classes in favor of a more integrated approach with `MicroscopyRig`

## Features
### NWB TAB reviews Issue[#48](https://github.com/catalystneuro/ndx-microscopy/issues/48)
- Added `MicroscopyChannel` object Sub-Issue[#49](https://github.com/catalystneuro/ndx-microscopy/issues/49)
- Added `MicroscopyRig` object Sub-Issue[#51](https://github.com/catalystneuro/ndx-microscopy/issues/51)
- Changed `Microscope` to inherit from `DeviceInstance` instead of `Device` Sub-Issue[#51](https://github.com/catalystneuro/ndx-microscopy/issues/51)
- Added `MicroscopeModel` that inherit from `DeviceModel` Sub-Issue[#51](https://github.com/catalystneuro/ndx-microscopy/issues/51)
- Updated `MicroscopySeries` to use `MicroscopyRig` instead of individual `microscope`, `excitation_light_path`, and `emission_light_path` references Sub-Issue[#51](https://github.com/catalystneuro/ndx-microscopy/issues/51)
- Added `dimensions_in_pixels` to `PlanarImagingSpace` and `dimensions_in_voxels` to `VolumetricImagingSpace` object Sub-Issue[#52](https://github.com/catalystneuro/ndx-microscopy/issues/52)
- Added `MultiChannelMicroscopyContainer` object Sub-Issue[#53](https://github.com/catalystneuro/ndx-microscopy/issues/53)
- Refactored segmentation classes: Sub-Issue[#56](https://github.com/catalystneuro/ndx-microscopy/issues/56)
  - Renamed `Segmentation2D` to `PlanarSegmentation`
  - Renamed `Segmentation3D` to `VolumetricSegmentation`
- Added `get_FOV_size()` method to both `PlanarImagingSpace` and `VolumetricImagingSpace` classes for calculating Field of View size in micrometers Sub-Issue[#53](https://github.com/catalystneuro/ndx-microscopy/issues/53)
- Added `microscopy_series` link to `MicroscopyResponseSeries` class Sub-Issue[#58](https://github.com/catalystneuro/ndx-microscopy/issues/58)
- Changed `image_to_voxel` in `volume_to_voxel`, `voxel_to_image` in `voxel_to_volume`, and `image_mask` in `volume_mask` in VolumetricSegmentation Sub-Issue[#57](https://github.com/catalystneuro/ndx-microscopy/issues/57)

# v0.2.1 (March 28, 2025)

## Bug Fixes

# v0.2.0 (March 19, 2025)

## Deprecations and Changes
- Change `grid_spacing_in_um` in `pixel_size_in_um` and `voxel_size_in_um` (and relative doc string) to better represent the physical dimension of the fundamental unit of the image (pixel or voxel).

## Bug Fixes

## Features

## Improvements
- New illumination pattern classes to represent different microscopy scanning methods:
  - `IlluminationPattern`: Base class for describing the illumination pattern used to acquire images
  - `LineScan`: Line scanning method commonly used in two-photon microscopy
  - `PlaneAcquisition`: Whole plane acquisition method, common for light sheet and one-photon techniques
  - `RandomAccessScan`: Random access method for targeted, high-speed imaging of specific regions

- Added `technique` attribute to the `Microscope` class to describe the imaging technique used

- Updated `ImagingSpace` classes to include an `illumination_pattern` parameter, creating a direct link between the imaging space and the acquisition method

- Added mock implementations for all new classes in `_mock.py` for testing purposes

- Updated example notebooks to demonstrate the use of different scanning methods

## Notes

- These changes are backward compatible and add new functionality without removing existing features
- The `illumination_pattern` parameter is now required when creating `ImagingSpace` objects
