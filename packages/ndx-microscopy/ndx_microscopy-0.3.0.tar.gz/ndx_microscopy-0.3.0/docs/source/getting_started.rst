.. _getting_started:

***************
Getting Started
***************

Prerequisites
============

Before installing ndx-microscopy, ensure you have:

- Python 3.7 or later
- PyNWB installed
- ndx-ophys-devices extension installed (required for optical components)

Installation
===========

Python Installation
-----------------

The ndx-microscopy extension can be installed via pip:

.. code-block:: bash

   pip install ndx-microscopy

This will automatically install all required dependencies.

Basic Concepts
============

The ndx-microscopy extension provides a standardized way to store and organize microscopy data in the NWB format. Here are the key components:

Device Components
---------------
- **MicroscopeModel**: Defines the model of a microscope
- **Microscope**: The primary device instance used for imaging
  - Includes technique specification (e.g., scan mirrors, light sheet, widefield)
- **MicroscopyRig**: Organizes all optical components in a single container
- Other optical components (from ndx-ophys-devices):
    - ExcitationSource (lasers, LEDs)
    - OpticalFilter (bandpass, edge filters)
    - Photodetector (PMTs, cameras)
    - DichroicMirror
    - Indicator (fluorescent proteins, dyes)

Illumination Patterns
-----------------
- **IlluminationPattern**: Base class for describing how the sample is illuminated
- **LineScan**: For line scanning methods (common in two-photon microscopy)
- **PlaneAcquisition**: For whole plane acquisition (common in light sheet and one-photon)
- **RandomAccessScan**: For targeted, high-speed imaging of specific regions

Imaging Spaces
------------
- **PlanarImagingSpace**: For 2D imaging (single plane)
- **VolumetricImagingSpace**: For 3D imaging (z-stacks)
- Includes physical coordinates, grid spacing, and reference frames
- Requires an illumination pattern to specify how the space was scanned

Data Series
----------
- **PlanarMicroscopySeries**: 2D time series data
- **VolumetricMicroscopySeries**: 3D time series data
- **MultiPlaneMicroscopyContainer**: Multiple imaging planes
- **MultiChannelMicroscopyContainer**: Multiple channel imaging data

Quick Start Example
================

Here's a minimal example showing how to create a basic microscopy dataset:

.. code-block:: python

    from datetime import datetime
    from uuid import uuid4
    from pynwb import NWBFile
    from ndx_microscopy import (
        MicroscopeModel,
        Microscope, 
        MicroscopyRig,
        PlanarImagingSpace,
        PlanarMicroscopySeries,
        LineScan
    )
    from ndx_ophys_devices import (
        ExcitationSourceModel,
        ExcitationSource,
        BandOpticalFilterModel,
        BandOpticalFilter,
        DichroicMirrorModel,
        DichroicMirror,
        PhotodetectorModel,
        Photodetector,
        Indicator
    )
    import numpy as np

    # Create NWB file
    nwbfile = NWBFile(
        session_description='Example microscopy session',
        identifier=str(uuid4()),
        session_start_time=datetime.now()
    )

    # Set up microscope model
    microscope_model = MicroscopeModel(
        name='2p-model',
        description='Two-photon microscope model',
        model_number='2p-001',
        manufacturer='ImagingTech'
    )
    nwbfile.add_device(microscope_model)

    # Set up microscope with technique
    microscope = Microscope(
        name='2p-scope',
        description='Custom two-photon microscope',
        serial_number='2p-serial-001',
        model=microscope_model,
        technique='mirror scanning'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    # Create indicator
    indicator = Indicator(
        name='gcamp6f',
        label='GCaMP6f',
        description='Calcium indicator'
    )

    # Create example optical component models
    excitation_source_model = ExcitationSourceModel(
        name="excitation_source_model",
        manufacturer="Laser Manufacturer",
        model_number="ES-123",
        description="Excitation source model",
        source_type="laser",
        excitation_mode="two-photon",
        wavelength_range_in_nm=[800.0, 1000.0]
    )
    nwbfile.add_device(excitation_source_model)
    
    excitation_filter_model = BandOpticalFilterModel(
        name="excitation_filter_model",
        filter_type="Bandpass",
        manufacturer="Semrock",
        model_number="FF01-920/80",
        center_wavelength_in_nm=920.0,
        bandwidth_in_nm=80.0
    )
    nwbfile.add_device(excitation_filter_model)
    
    dichroic_mirror_model = DichroicMirrorModel(
        name="dichroic_mirror_model",
        manufacturer="Semrock",
        model_number="FF757-Di01",
        cut_on_wavelength_in_nm=757.0
    )
    nwbfile.add_device(dichroic_mirror_model)
    
    photodetector_model = PhotodetectorModel(
        name="photodetector_model",
        detector_type="PMT",
        manufacturer="Hamamatsu",
        model_number="R6357",
        gain=70.0,
        gain_unit="dB"
    )
    nwbfile.add_device(photodetector_model)
    
    emission_filter_model = BandOpticalFilterModel(
        name="emission_filter_model",
        filter_type="Bandpass",
        manufacturer="Semrock",
        model_number="FF01-510/84",
        center_wavelength_in_nm=510.0,
        bandwidth_in_nm=84.0
    )
    nwbfile.add_device(emission_filter_model)

    # Create optical component instances
    laser = ExcitationSource(
        name='laser',
        description='Two-photon excitation laser',
        serial_number="ES-SN-123456",
        model=excitation_source_model,
        intensity_in_W_per_m2=1000.0,
        exposure_time_in_s=0.001
    )
    nwbfile.add_device(laser)

    ex_filter = BandOpticalFilter(
        name='ex_filter',
        description='Excitation filter',
        serial_number="EF-SN-123456",
        model=excitation_filter_model
    )
    nwbfile.add_device(ex_filter)

    dichroic = DichroicMirror(
        name='dichroic',
        description='Dichroic mirror',
        serial_number="DM-SN-123456",
        model=dichroic_mirror_model
    )
    nwbfile.add_device(dichroic)

    detector = Photodetector(
        name='detector',
        description='PMT detector',
        serial_number="PD-SN-123456",
        model=photodetector_model
    )
    nwbfile.add_device(detector)

    em_filter = BandOpticalFilter(
        name='em_filter',
        description='Emission filter',
        serial_number="EF-SN-123456",
        model=emission_filter_model
    )
    nwbfile.add_device(em_filter)

    # Create microscopy rig
    microscopy_rig = MicroscopyRig(
        name='2p_rig',
        description='Two-photon microscopy rig',
        microscope=microscope,
        excitation_source=laser,
        excitation_filter=ex_filter,
        dichroic_mirror=dichroic,
        photodetector=detector,
        emission_filter=em_filter
    )

    # Define illumination pattern
    line_scan = LineScan(
        name='line_scanning',
        description='Line scanning two-photon microscopy',
        scan_direction='horizontal',
        line_rate_in_Hz=1000.0,
        dwell_time_in_s=1.0e-6
    )

    # Define imaging space with illumination pattern
    planar_imaging_space = PlanarImagingSpace(
        name='cortex_plane',
        description='Layer 2/3 of visual cortex',
        pixel_size_in_um=[1.0, 1.0],
        dimensions_in_pixels=[512, 512],
        origin_coordinates=[-1.2, -0.6, -2.0],
        illumination_pattern=line_scan  # Include the illumination pattern
    )

    # Create example imaging data
    data = np.random.rand(100, 512, 512)  # 100 frames, 512x512 pixels

    # Create imaging series
    microscopy_series = PlanarMicroscopySeries(
        name='imaging_data',
        microscopy_rig=microscopy_rig,
        planar_imaging_space=planar_imaging_space,
        data=data,
        unit='a.u.',
        rate=30.0,
        starting_time=0.0,
    )
    nwbfile.add_acquisition(microscopy_series)

    # Save file
    from pynwb import NWBHDF5IO
    with NWBHDF5IO('microscopy_session.nwb', 'w') as io:
        io.write(nwbfile)

Next Steps
=========

After getting familiar with the basics:

1. Check out the :ref:`examples` section for more detailed examples including:
   - Volumetric imaging
   - Multi-plane imaging
   - ROI segmentation and response series

2. Read the :ref:`user_guide` for best practices and detailed workflows

3. Review the :ref:`api` documentation for complete reference

4. See the :ref:`format` section to understand the underlying data organization
