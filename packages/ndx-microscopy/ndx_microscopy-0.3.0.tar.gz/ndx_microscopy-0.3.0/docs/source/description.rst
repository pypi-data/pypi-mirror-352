.. _description:

Overview
========

The ndx-microscopy extension for NWB provides a standardized way to store and organize microscopy data in neuroscience research. This extension integrates with `ndx-ophys-devices <https://github.com/catalystneuro/ndx-ophys-devices>`_ to provide comprehensive optical component specifications and supports various microscopy techniques while maintaining detailed metadata about the imaging setup, experimental conditions, and acquired data.

Key Features
----------

Device and Optical Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^
- MicroscopeModel for defining microscope models
- Microscope instances with technique specifications
- MicroscopyRig for organizing optical components
- Integration with ndx-ophys-devices for:
    - Excitation sources (continuous and pulsed)
    - Optical filters (band and edge types)
    - Dichroic mirrors
    - Photodetectors
    - Fluorescent indicators

Illumination Pattern Support
^^^^^^^^^^^^^^^^^^^^^
- Base illumination pattern class for general use cases
- Line scanning for high-speed XY raster scanning acquisition
- Plane acquisition for light sheet and widefield techniques
- Random access scanning for targeted region imaging
- Detailed scanning parameters (rates, directions, dwell times)

Imaging Space Management
^^^^^^^^^^^^^^^^^^^^^
- 2D planar imaging spaces
- 3D volumetric imaging spaces
- Precise coordinate system handling
- Reference frame management
- Grid spacing and resolution tracking
- Integration with illumination patterns

Data Organization
^^^^^^^^^^^^^
- Time series data for both 2D and 3D imaging
- Multi-plane imaging support
- Variable depth imaging capabilities
- Multi-channel data handling
- ROI/segmentation organization
- Response data storage

Data Structure
------------

The extension organizes microscopy data hierarchically::

    nwbfile
    ├── devices
    │   ├── microscope_model: MicroscopeModel
    │   └── microscope: Microscope
    ├── acquisition
    │   └── MicroscopySeries
    │       └── microscopy_rig: MicroscopyRig
    └── processing
        └── ophys
            ├── MicroscopyResponseSeriesContainer
            └── SegmentationContainer

Common Applications
----------------

Calcium Imaging
^^^^^^^^^^^^^
- GCaMP and other calcium indicator imaging
- Both one-photon and multi-photon implementations
- ROI segmentation
- Fluorescence time series data

Voltage Imaging
^^^^^^^^^^^^^
- Direct measurement of neural activity
- Voltage-sensitive fluorescent proteins/dyes
- High-speed imaging capabilities
- High temporal resolution data

For Developers
------------

The extension is open source and welcomes contributions:

- Source code: `GitHub Repository <https://github.com/catalystneuro/ndx-microscopy>`_
- Issue tracking and feature requests
- Development guidelines
- Contributing instructions

Extension Design:
- Integration with ndx-ophys-devices
- Comprehensive test suite
- Extensible architecture
