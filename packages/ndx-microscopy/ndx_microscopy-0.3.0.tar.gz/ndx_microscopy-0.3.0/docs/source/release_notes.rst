.. _release_notes:

*************
Release Notes
*************
Version 0.3.0 (Jun 3, 2025)
==============================

Deprecations and Changes
-------------------------

* Removed `ExcitationLightPath` and `EmissionLightPath` classes in favor of a more integrated approach with `MicroscopyRig`
* Changed `Microscope` to inherit from `DeviceInstance` instead of `Device`
* Updated `MicroscopySeries` to use `MicroscopyRig` instead of individual `microscope`, `excitation_light_path`, and `emission_light_path` references
* Refactored segmentation classes:
  * Renamed ``Segmentation2D`` to ``PlanarSegmentation``
  * Renamed ``Segmentation3D`` to ``VolumetricSegmentation``
* Changed `image_to_voxel` in `volume_to_voxel`
* Changed `voxel_to_image` in `voxel_to_volume`
* Changed `image_mask` in `volume_mask` in VolumetricSegmentation

Features
--------

* Added `MicroscopeModel` class to define microscope models (inherits from `DeviceModel`)
* Added `MicroscopyRig` class to organize all optical components in a single container, including:
  * `microscope`: Link to the Microscope instance
  * `excitation_source`: Link to ExcitationSource (optional)
  * `excitation_filter`: Link to OpticalFilter (optional)
  * `dichroic_mirror`: Link to DichroicMirror (optional)
  * `photodetector`: Link to Photodetector (optional)
  * `emission_filter`: Link to OpticalFilter (optional)
* Added `MicroscopyChannel` class to represent a single channel in a microscopy series, which includes:
  * `excitation_wavelength`: Excitation wavelength for the channel
  * `emission_wavelength`: Emission wavelength for the channel 
  * `indicator`: Link to Indicator
* Added `MultiChannelMicroscopyContainer` class to support multi-channel imaging data.
  * This class allows for the storage of multiple `MicroscopySeries` objects, each representing a different channel of imaging data.
  * It provides methods to access and manipulate individual channels, facilitating the analysis of multi-channel datasets.
* Added `dimensions_in_pixels` to `PlanarImagingSpace` and `dimensions_in_voxels` to `VolumetricImagingSpace`
* Added `get_FOV_size()` method to both `PlanarImagingSpace` and `VolumetricImagingSpace` classes for calculating Field of View size in micrometers
* Added `microscopy_series` link to `MicroscopyResponseSeries` class to point the `MicroscopySeries` this response series is derived from.


Improvements
------------

* Simplified the optical path configuration by consolidating components into a single `MicroscopyRig` container
* Improved organization of device components with the addition of `MicroscopeModel` and clearer inheritance structure
* Updated all documentation and examples to reflect the new structure

Notes
------

* These changes are NOT backward compatible and require updating existing code to use the new structure
* The `MicroscopyRig` approach provides a more flexible and intuitive way to organize optical components
* Improved organization of multi channel imaging data

Version 0.2.0 (March 19, 2025)
==============================

Deprecations and Changes
-------------------------

* Change `grid_spacing_in_um` in `pixel_size_in_um` and `voxel_size_in_um` (and relative doc string) to better represent the physical dimension of the fundamental unit of the image (pixel or voxel).

## Bug Fixes

## Features

Improvements
------------

* New illumination pattern classes to represent different microscopy scanning methods:
  * `IlluminationPattern`: Base class for describing the illumination pattern used to acquire images
  * `LineScan`: Line scanning method commonly used in two-photon microscopy
  * `PlaneAcquisition`: Whole plane acquisition method, common for light sheet and one-photon techniques
  * `RandomAccessScan`: Random access method for targeted, high-speed imaging of specific regions
* Added `technique` attribute to the `Microscope` class to describe the imaging technique used
* Updated `ImagingSpace` classes to include an `illumination_pattern` parameter, creating a direct link between the imaging space and the acquisition method
* Added mock implementations for all new classes in `_mock.py` for testing purposes
* Updated example notebooks to demonstrate the use of different scanning methods

 Notes
------

* These changes are backward compatible and add new functionality without removing existing features
* The `illumination_pattern` parameter is now required when creating `ImagingSpace` objects

Version 0.1.0 (March 10, 2025)
============

Initial release of ndx-microscopy extension.

Features
--------

* Microscope metadata: ``Microscope``
* Integration with ndx-ophys-devices for optical component specifications: ``ExcitationSource``/``PulsedExcitationSource``, ``BandOpticalFilter``/``EdgeOpticalFilter``, ``DichroicMirror``, ``Photodetector``, ``Indicator``
* Advanced light path configurations: ``ExcitationLightPath``, ``EmissionLightPath`` 
* Imaging space definitions: ``PlanarImagingSpace``, ``VolumetricImagingSpace``
* Support for 2D and 3D imaging: ``PlanarMicroscopySeries``, ``VolumetricMicroscopySeries``, ``MultiPlaneMicroscopyContainer``
* ROI/segmentation storage: ``SummaryImages``, ``PlanarSegmentation``, ``VolumetricSegmentation``, ``SegmentationContainer``, ``MicroscopyResponseSeries``, ``MicroscopyResponseSeriesContainer``
* Abstract Neurodata types: ``ImagingSpace``, ``MicroscopySeries``, ``Segmentation``

Changes
-------

* Initial implementation of all neurodata data types
* Basic documentation and examples
* Integration tests and validation
