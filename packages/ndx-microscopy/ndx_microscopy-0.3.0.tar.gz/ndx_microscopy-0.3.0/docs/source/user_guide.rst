.. _user_guide:

**********
User Guide
**********

This guide provides detailed information about using the ndx-microscopy extension effectively.

Core Concepts
-----------

Device Components
^^^^^^^^^^^^^^^

The device components include MicroscopeModel, Microscope, and MicroscopyRig:

1. **MicroscopeModel**: Defines the model of a microscope

   .. code-block:: python

       microscope_model = MicroscopeModel(
           name='2p-model',
           description='Two-photon microscope model',
           model_number='2p-001',
           manufacturer='ImagingTech'
       )
       nwbfile.add_device(microscope_model)

2. **Microscope**: Defines an instance of a microscope

   .. code-block:: python

       microscope = Microscope(
           name='2p-scope',
           description='Custom two-photon microscope',
           serial_number='2p-serial-001',
           model=microscope_model,
           technique='mirror scanning'  # Specify the technique used
       )
       nwbfile.add_device(microscope)

3. **MicroscopyRig**: Defines a collection of devices that make up the microscopy rig

   .. code-block:: python

       # Create optical component models using ndx-ophys-devices
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

       # Create the microscopy rig
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

Other optical components (filters, sources, detectors) are provided by the ndx-ophys-devices extension.

4. **MicroscopyChannel**: Defines a channel with indicator and wavelength information

   .. code-block:: python

       microscopy_channel = MicroscopyChannel(
           name='gcamp_channel',
           description='GCaMP6f channel',
           excitation_wavelength_in_nm=488.0,
           emission_wavelength_in_nm=520.0,
           indicator=indicator               # from ndx-ophys-devices
       )

Illumination Pattern Configuration
^^^^^^^^^^^^^^^^^^^^^

Illumination patterns define how the microscope scans or illuminates the sample:

1. **IlluminationPattern**: Base class for general use cases

   .. code-block:: python

       illumination_pattern = IlluminationPattern(
           name='custom_pattern',
           description='Custom illumination pattern'
       )

2. **LineScan**: For line scanning methods (common in two-photon microscopy)

   .. code-block:: python

       line_scan = LineScan(
           name='line_scanning',
           description='Line scanning two-photon microscopy',
           scan_direction='horizontal',  # or 'vertical'
           line_rate_in_Hz=1000.0,       # lines per second
           dwell_time_in_s=1.0e-6        # time spent at each point
       )

3. **PlaneAcquisition**: For whole plane acquisition (common in light sheet and one-photon)

   .. code-block:: python

       plane_acquisition = PlaneAcquisition(
           name='plane_acquisition',
           description='Widefield fluorescence imaging',
           point_spread_function_in_um="32 um ± 1.6 um",
           illumination_angle_in_degrees=45.0,  # for light sheet
           plane_rate_in_Hz=100.0               # planes per second
       )

4. **RandomAccessScan**: For targeted, high-speed imaging of specific regions

   .. code-block:: python

       random_access_scan = RandomAccessScan(
           name='random_access',
           description='Targeted imaging of specific neurons',
           max_scan_points=1000,
           dwell_time_in_s=1.0e-6,
           scanning_pattern='spiral'  # or other pattern description
       )

Imaging Space Definition
^^^^^^^^^^^^^^^^^^^^^

Imaging spaces define the physical region being imaged:

1. **PlanarImagingSpace**: For 2D imaging

   .. code-block:: python

       # First define an illumination pattern
       line_scan = LineScan(
           name='line_scanning',
           description='Line scanning two-photon microscopy',
           scan_direction='horizontal',
           line_rate_in_Hz=1000.0,
           dwell_time_in_s=1.0e-6
       )
       
       # Then create the imaging space with the illumination pattern
       space_2d = PlanarImagingSpace(
           name='cortex_plane',
           description='Layer 2/3 of visual cortex',
           pixel_size_in_um=[1.0, 1.0],        # x, y spacing
           dimensions_in_pixels=[512, 512],    # width, height in pixels
           origin_coordinates=[-1.2, -0.6, -2.0], # relative to bregma
           location='Visual cortex',
           reference_frame='bregma',
           orientation='RAS',                    # Right-Anterior-Superior
           illumination_pattern=line_scan        # Include the illumination pattern
       )

2. **VolumetricImagingSpace**: For 3D imaging

   .. code-block:: python

       # First define an illumination pattern
       plane_acquisition = PlaneAcquisition(
           name='plane_acquisition',
           description='Light sheet imaging',
           point_spread_function_in_um="32 um ± 1.6 um",
           illumination_angle_in_degrees=45.0,
           plane_rate_in_Hz=100.0
       )
       
       # Then create the imaging space with the illumination pattern
       space_3d = VolumetricImagingSpace(
           name='cortex_volume',
           description='Visual cortex volume',
           voxel_size_in_um=[1.0, 1.0, 2.0],   # x, y, z spacing
           dimensions_in_voxels=[512, 512, 100], # width, height, depth in voxels
           origin_coordinates=[-1.2, -0.6, -2.0],
           location='Visual cortex',
           reference_frame='bregma',
           orientation='RAS',
           illumination_pattern=plane_acquisition
       )

Common Workflows
-------------

2D Imaging
^^^^^^^^^

Basic workflow for 2D imaging:

.. code-block:: python

    # 1. Set up microscope model and instance
    microscope_model = MicroscopeModel(
        name='2p-model',
        description='Two-photon microscope model',
        model_number='2p-001',
        manufacturer='ImagingTech'
    )
    nwbfile.add_device(microscope_model)

    microscope = Microscope(
        name='2p-scope',
        description='Custom two-photon microscope',
        serial_number='2p-serial-001',
        model=microscope_model,
        technique='mirror scanning'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    # 2. Create optical component models and instances
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
    
    laser = ExcitationSource(
        name='laser',
        description='Two-photon excitation laser',
        serial_number="ES-SN-123456",
        model=excitation_source_model,
        intensity_in_W_per_m2=1000.0,
        exposure_time_in_s=0.001
    )
    nwbfile.add_device(laser)

    # Add other optical components (filters, detectors, etc.)
    # ...

    # 3. Create the microscopy rig
    microscopy_rig = MicroscopyRig(
        name='2p_rig',
        description='Two-photon microscopy rig',
        microscope=microscope,
        excitation_source=laser,
        # Add other optical components
        # ...
    )

    # 4. Define illumination pattern
    line_scan = LineScan(
        name='line_scanning',
        description='Line scanning two-photon microscopy',
        scan_direction='horizontal',
        line_rate_in_Hz=1000.0,
        dwell_time_in_s=1.0e-6
    )

    # 5. Set up imaging space with illumination pattern
    planar_imaging_space = PlanarImagingSpace(
        name='cortex_plane',
        description='Layer 2/3 of visual cortex',
        pixel_size_in_um=[1.0, 1.0],        # x, y spacing
        dimensions_in_pixels=[512, 512],    # width, height in pixels
        origin_coordinates=[-1.2, -0.6, -2.0], # relative to bregma
        location='Visual cortex',
        reference_frame='bregma',
        orientation='RAS',                    # Right-Anterior-Superior
        illumination_pattern=line_scan        # Include the illumination pattern
    )

    # 4. Create microscopy channel
    microscopy_channel = MicroscopyChannel(
        name='gcamp_channel',
        description='GCaMP6f channel',
        excitation_wavelength_in_nm=488.0,
        emission_wavelength_in_nm=520.0,
        indicator=indicator               # from ndx-ophys-devices
    )

    # 5. Create imaging series
    microscopy_series = PlanarMicroscopySeries(
        name='microscopy_series',
        description='Two-photon calcium imaging',
        microscopy_rig=microscopy_rig,
        microscopy_channel=microscopy_channel,
        planar_imaging_space=planar_imaging_space,
        data=data,                # [frames, height, width]
        unit='a.u.',
        rate=30.0,
        starting_time=0.0,
    )
    nwbfile.add_acquisition(microscopy_series)

One-Photon Imaging with Plane Acquisition
^^^^^^^^^

Workflow for one-photon widefield imaging:

.. code-block:: python

    # 1. Set up microscope model and instance
    microscope_model = MicroscopeModel(
        name='1p-model',
        description='One-photon microscope model',
        model_number='1p-001',
        manufacturer='ImagingTech'
    )
    nwbfile.add_device(microscope_model)

    microscope = Microscope(
        name='1p-scope',
        description='Custom one-photon microscope',
        serial_number='1p-serial-001',
        model=microscope_model,
        technique='widefield'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    # 2. Create optical component models and instances
    # ...

    # 3. Create the microscopy rig
    microscopy_rig = MicroscopyRig(
        name='1p_rig',
        description='One-photon microscopy rig',
        microscope=microscope,
        # Add optical components
        # ...
    )

    # 4. Define illumination pattern
    plane_acquisition = PlaneAcquisition(
        name='plane_acquisition',
        description='Widefield fluorescence imaging',
        point_spread_function_in_um="32 um ± 1.6 um",
        plane_rate_in_Hz=30.0
    )

    # 5. Set up imaging space with illumination pattern
    planar_imaging_space = PlanarImagingSpace(
        name='hippo_plane',
        description='CA1 region of hippocampus',
        pixel_size_in_um=[1.0, 1.0],
        dimensions_in_pixels=[512, 512],  # width, height in pixels
        origin_coordinates=[-1.8, 2.0, 1.2],
        location='Hippocampus, CA1 region',
        reference_frame='bregma',
        orientation='RAS',
        illumination_pattern=plane_acquisition
    )

    # 6. Create microscopy channel
    microscopy_channel = MicroscopyChannel(
        name='gcamp_channel',
        description='GCaMP6f channel',
        excitation_wavelength_in_nm=470.0,
        emission_wavelength_in_nm=520.0,
        indicator=indicator               # from ndx-ophys-devices
    )

    # 5. Create imaging series
    microscopy_series = PlanarMicroscopySeries(
        name='imaging_data',
        description='One-photon calcium imaging',
        microscopy_channel=microscopy_channel,
        microscopy_rig=microscopy_rig,
        planar_imaging_space=planar_imaging_space,
        data=data,
        unit='a.u.',
        rate=30.0,
        starting_time=0.0
    )
    nwbfile.add_acquisition(microscopy_series)

3D Imaging with Random Access Scanning
^^^^^^^^^

Workflow for volumetric imaging with targeted scanning:

.. code-block:: python

    # 1. Set up microscope model and instance
    microscope_model = MicroscopeModel(
        name='volume-model',
        description='Volumetric imaging microscope model',
        model_number='volume-001',
        manufacturer='ImagingTech'
    )
    nwbfile.add_device(microscope_model)

    microscope = Microscope(
        name='volume-scope',
        description='Custom volumetric imaging microscope',
        serial_number='volume-serial-001',
        model=microscope_model,
        technique='acousto-optical deflectors'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    # 2. Create optical component models and instances
    # ...

    # 3. Create the microscopy rig
    microscopy_rig = MicroscopyRig(
        name='volume_rig',
        description='Volumetric microscopy rig',
        microscope=microscope,
        # Add optical components
        # ...
    )

    # 4. Define illumination pattern
    random_access_scan = RandomAccessScan(
        name='random_access',
        description='Targeted imaging of specific neurons',
        max_scan_points=1000,
        dwell_time_in_s=1.0e-6,
        scanning_pattern='spiral'
    )

    # 5. Set up volumetric space with illumination pattern
    volumetric_imaging_space = VolumetricImagingSpace(
        name='cortex_volume',
        description='Visual cortex volume',
        voxel_size_in_um=[1.0, 1.0, 2.0],   # x, y, z spacing
        dimensions_in_voxels=[512, 512, 100], # width, height, depth in voxels
        origin_coordinates=[-1.2, -0.6, -2.0],
        location='Visual cortex',
        reference_frame='bregma',
        orientation='RAS',
        illumination_pattern=random_access_scan
    )

    # 6. Create microscopy channel
    microscopy_channel = MicroscopyChannel(
        name='gcamp_channel',
        description='GCaMP6f channel',
        excitation_wavelength_in_nm=920.0,
        emission_wavelength_in_nm=520.0,
        indicator=indicator               # from ndx-ophys-devices
    )

    # 5. Create volumetric series
    volume_series = VolumetricMicroscopySeries(
        name='volume_data',
        microscopy_rig=microscopy_rig,
        microscopy_channel=microscopy_channel,
        volumetric_imaging_space=volumetric_imaging_space,
        data=data,                # [frames, height, width, depths]
        unit='a.u.',
        rate=5.0,
        starting_time=0.0,
    )
    nwbfile.add_acquisition(volume_series)

ROI Segmentation
^^^^^^^^^^^^^

Workflow for ROI segmentation:

.. code-block:: python

    # 1. Create summary images
    mean_image = SummaryImage(
        name='mean',
        description='Mean intensity projection',
        data=np.mean(data, axis=0)
    )

    # 2. Create segmentation
    segmentation = PlanarSegmentation(
        name='rois',
        description='Manual ROI segmentation',
        planar_imaging_space=imaging_space,
        summary_images=[mean_image]
    )

    # 3. Add ROIs using image masks
    roi_mask = np.zeros((height, width), dtype=bool)
    roi_mask[256:266, 256:266] = True
    segmentation.add_roi(image_mask=roi_mask)

    # 4. Add ROIs using pixel masks
    pixel_mask = [
        [100, 100, 1.0],  # x, y, weight
        [101, 100, 1.0],
        [102, 100, 1.0]
    ]
    segmentation.add_roi(pixel_mask=pixel_mask)

Response Data Storage
^^^^^^^^^^^^^^^^^

Workflow for storing ROI responses:

.. code-block:: python

    # 1. Create ROI region
    roi_region = segmentation.create_roi_table_region(
        description='All ROIs',
        region=list(range(len(segmentation.id)))
    )

    # 2. Create response series
    response_series = MicroscopyResponseSeries(
        name='roi_responses',
        description='Fluorescence responses',
        data=responses,
        rois=roi_region,
        unit='n.a.',
        rate=30.0,
        starting_time=0.0,
    )

Best Practices
-----------

Data Organization
^^^^^^^^^^^^^

1. **Naming Conventions**
   - Use descriptive, consistent names
   - Include relevant metadata in descriptions
   - Document coordinate systems and reference frames

2. **Data Structure**
   - Group related data appropriately
   - Maintain clear relationships between raw and processed data
   - Include all necessary metadata
