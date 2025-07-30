*******
Format
*******

The ndx-microscopy extension defines several neurodata types to represent microscopy data and metadata in a standardized way. This extension integrates with `ndx-ophys-devices <https://github.com/catalystneuro/ndx-ophys-devices>`_ to provide comprehensive optical component specifications.

Device Components
---------------

MicroscopeModel
^^^^^^^^^^^^^^^
A microscope model used to acquire imaging data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MicroscopeModel
        neurodata_type_inc: DeviceModel
        doc: A microscope model used to acquire imaging data.

Microscope
^^^^^^^^^
A device instance for acquiring imaging data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: Microscope
        neurodata_type_inc: DeviceInstance
        doc: Instance of a microscope used to acquire imaging data.
        attributes:
          - name: technique
            dtype: text
            doc: Imaging technique used by the microscope (e.g. scan mirrors, light sheet, temporal focusing, acusto-optical modulation, piezo z-scan mirrors).
            required: false

MicroscopyRig
^^^^^^^^^^^^^
A collection of devices and metadata that make up the microscopy rig.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MicroscopyRig
        neurodata_type_inc: NWBContainer
        doc: A collection of devices and metadata that make up the microscopy rig.
        attributes:
          - name: description
            dtype: text
            doc: Description of the microscopy rig.
        links:
          - name: microscope
            target_type: Microscope
            doc: Link to Microscope object which contains metadata about the microscope used to acquire imaging data.
            quantity: 1
          - name: excitation_source
            target_type: ExcitationSource
            doc: Link to ExcitationSource object which contains metadata about the excitation source device. If it is a pulsed excitation source link a PulsedExcitationSource object.
            quantity: "?"
          - name: excitation_filter
            target_type: OpticalFilter
            doc: Link to OpticalFilter object which contains metadata about the excitation filter. It can be either a BandOpticalFilter (e.g., 'Bandpass', 'Bandstop', 'Longpass', 'Shortpass') or a EdgeOpticalFilter (Longpass or Shortpass).
            quantity: "?"
          - name: dichroic_mirror
            target_type: DichroicMirror
            doc: Link to DichroicMirror object which contains metadata about the dichroic mirror.
            quantity: "?"
          - name: photodetector
            target_type: Photodetector
            doc: Link to Photodetector object which contains metadata about the photodetector device.
            quantity: "?"
          - name: emission_filter
            target_type: OpticalFilter
            doc: Link to OpticalFilter object which contains metadata about the emission filter. It can be either a BandOpticalFilter (e.g., 'Bandpass', 'Bandstop', 'Longpass', 'Shortpass') or a EdgeOpticalFilter (Longpass or Shortpass).
            quantity: "?"

For other device components (ExcitationSource, OpticalFilter, Photodetector, etc.), please refer to the `ndx-ophys-devices documentation <https://ndx-ophys-devices.readthedocs.io/>`_.

MicroscopyChannel
^^^^^^^^^^^^^^^
Represents a channel in a microscope with metadata about the indicator and wavelengths.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MicroscopyChannel
        neurodata_type_inc: NWBContainer
        doc: A channel in a microscope that contains metadata about the indicator, the excitation and emission wavelengths.
        attributes:
          - name: name
            dtype: text
            doc: Name of the channel.
          - name: description
            dtype: text
            doc: Description of the channel.
            required: false
          - name: excitation_wavelength_in_nm
            dtype: float64
            doc: Wavelength of the excitation light in nanometers.
          - name: emission_wavelength_in_nm
            dtype: float64
            doc: Wavelength of the emission light in nanometers.
        groups:
          - neurodata_type_inc: Indicator
            doc: Indicator object which contains metadata about the indicator used in this light path.
            quantity: 1

Microscopy Series Components
------------------------

MicroscopySeries
^^^^^^^^^^^^^
Base type for microscopy time series data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MicroscopySeries
        neurodata_type_inc: TimeSeries
        doc: Imaging data acquired over time from an optical channel in a microscope while a light source illuminates the
          imaging space.
        groups:
          - neurodata_type_inc: MicroscopyRig
            doc: MicroscopyRig object containing metadata about the microscopy rig used to acquire this imaging data.
            quantity: 1
          - neurodata_type_inc: MicroscopyChannel
            doc: MicroscopyChannel object containing metadata about the channel used to acquire this imaging data.
            quantity: 1

PlanarMicroscopySeries
^^^^^^^^^^^^^^^^^^^
For 2D time series data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: PlanarMicroscopySeries
        neurodata_type_inc: MicroscopySeries
        doc: Imaging data acquired over time from an optical channel in a microscope while a light source illuminates a
          planar imaging space.
        datasets:
          - name: data
            doc: Recorded imaging data, shaped by (number of frames, frame height, frame width).
            dtype: numeric
            dims:
              - frames
              - height
              - width
            shape:
              - null
              - null
              - null
        groups:
          - neurodata_type_inc: PlanarImagingSpace
            doc: PlanarImagingSpace object containing metadata about the region of physical space this imaging data
              was recorded from.

VolumetricMicroscopySeries
^^^^^^^^^^^^^^^^^^^^^^^
For 3D time series data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: VolumetricMicroscopySeries
        neurodata_type_inc: MicroscopySeries
        doc: Volumetric imaging data acquired over time from an optical channel in a microscope while a light source
          illuminates a volumetric imaging space.
          Assumes the number of depth scans used to construct the volume is regular.
        datasets:
          - name: data
            doc: Recorded imaging data, shaped by (number of frames, frame height, frame width, number of depth planes).
            dtype: numeric
            dims:
              - frames
              - height
              - width
              - depths
            shape:
              - null
              - null
              - null
              - null
        groups:
          - neurodata_type_inc: VolumetricImagingSpace
            doc: VolumetricImagingSpace object containing metadata about the region of physical space this imaging data
              was recorded from.

MultiPlaneMicroscopyContainer
^^^^^^^^^^^^^^^^^^^^^^^^^
Container for multiple PlanarMicroscopySeries.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MultiPlaneMicroscopyContainer
        neurodata_type_inc: NWBDataInterface
        default_name: MultiPlaneMicroscopyContainer
        doc: Imaging data acquired over several depths, regularly or irregularly spaced; for instance, when using an
          electrically tunable lens. Each depth scan is stored in a separate PlanarMicroscopySeries object.
        groups:
          - neurodata_type_inc: PlanarMicroscopySeries
            doc: PlanarMicroscopySeries object(s) containing imaging data for a single depth scan.
            quantity: "+"

MultiChannelMicroscopyContainer
^^^^^^^^^^^^^^^^^^^^^^^^^
Container for multiple PlanerMicroscopySeries or VolumetricMicroscopySeries acquired from different channels.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MultiChannelMicroscopyContainer
        neurodata_type_inc: NWBDataInterface
        default_name: MultiChannelMicroscopyContainer
        doc:
          Imaging data acquired over several channels; for instance, when using multiple excitation wavelengths
          or multiple indicators. Each channel is stored in a separate PlanarMicroscopySeries or VolumetricMicroscopySeries object.
        groups:
          - neurodata_type_inc: MicroscopySeries
            doc: MicroscopySeries object containing imaging data for a single channel scan.
            quantity: "+"

Illumination Pattern Components
--------------------------

IlluminationPattern
^^^^^^^^^^^^^^^
Base class for describing the illumination pattern used to acquire the image.

.. code-block:: yaml

    groups:
      - neurodata_type_def: IlluminationPattern
        neurodata_type_inc: NWBContainer
        doc: Base class for describing the illumination pattern used to acquired the image. Use this object if the illumination pattern is not one of the specific types (e.g., Line, Plane, RandomAccess).
        attributes:
          - name: description
            dtype: text
            doc: General description of the illumination pattern used.
            required: false

LineScan
^^^^^^^
Line scanning method for microscopy.

.. code-block:: yaml

    groups:
      - neurodata_type_def: LineScan
        neurodata_type_inc: IlluminationPattern
        doc: Line scanning method.
        attributes:
          - name: scan_direction
            dtype: text
            doc: Direction of line scanning (horizontal or vertical).
            required: false
          - name: line_rate_in_Hz
            dtype: float64
            doc: Rate of line scanning in lines per second.
            required: false
          - name: dwell_time_in_s
            dtype: float64
            doc: Average time spent at each scanned point.
            required: false

PlaneAcquisition
^^^^^^^^^^^^^
Whole plane acquisition method for microscopy.

.. code-block:: yaml

    groups:
      - neurodata_type_def: PlaneAcquisition
        neurodata_type_inc: IlluminationPattern
        doc: Whole plane acquisition, common for light sheet techniques.
        attributes:
          - name: point_spread_function_in_um
            dtype: text
            doc: Estimated plane spatial profile or point spread function, expressed as mean [um] ± s.d [um].
            required: false
          - name: illumination_angle_in_degrees
            dtype: float64
            doc: Angle of illumination in degrees.
            required: false
          - name: plane_rate_in_Hz
            dtype: float64
            doc: Rate of plane acquisition in planes per second.
            required: false

RandomAccessScan
^^^^^^^^^^^^^
Random access scanning method for targeted imaging.

.. code-block:: yaml

    groups:
      - neurodata_type_def: RandomAccessScan
        neurodata_type_inc: IlluminationPattern
        doc: Random access method for targeted, high-speed imaging of specific regions.
        attributes:
          - name: max_scan_points
            dtype: numeric
            doc: Maximum number of points that can be scanned in a single frame.
            required: false
          - name: dwell_time_in_s
            dtype: float64
            doc: Average time spent at each scanned point.
            required: false
          - name: scanning_pattern
            dtype: text
            doc: Description of the point selection strategy.
            required: false

Imaging Space Components
--------------------

ImagingSpace
^^^^^^^^^^
Base type for metadata about the region being imaged.

.. code-block:: yaml

    groups:
      - neurodata_type_def: ImagingSpace
        neurodata_type_inc: NWBContainer
        doc: Abstract class to contain metadata about the region of physical space that imaging data was recorded from. Extended by PlanarImagingSpace and VolumetricImagingSpace.
        datasets:
          - name: origin_coordinates
            dtype: float64
            dims:
              - - x, y, z
            shape:
              - - 3
            doc:
              Physical location in stereotactic coordinates for the first element of the grid.
              See reference_frame to determine what the coordinates are relative to (e.g., bregma).
            quantity: "?"
            attributes:
              - name: unit
                dtype: text
                default_value: micrometers
                doc: Measurement units for origin coordinates. The default value is 'micrometers'.
        attributes:
          - name: description
            dtype: text
            doc: Description of the imaging space.
          - name: location
            dtype: text
            doc:
              General estimate of location in the brain being subset by this space.
              Specify the area, layer, etc.
              Use standard atlas names for anatomical regions when possible.
              Specify 'whole brain' if the entire brain is strictly contained within the space.
            required: false
          - name: reference_frame
            dtype: text
            doc:
              The reference frame for the origin coordinates. For example, 'bregma' or 'lambda' for rodent brains.
              If the origin coordinates are relative to a specific anatomical landmark, specify that here.
            required: false
          - name: orientation
            doc:
              "A 3-letter string. One of A,P,L,R,S,I for each of x, y, and z. For example, the most common
              orientation is 'RAS', which means x is right, y is anterior, and z is superior (a.k.a. dorsal).
              For dorsal/ventral use 'S/I' (superior/inferior). In the AnatomicalCoordinatesTable, an orientation of
              'RAS' corresponds to coordinates in the order of (ML (x), AP (y), DV (z))."
            dtype: text
            required: false
        groups:
          - neurodata_type_inc: IlluminationPattern
            doc: IlluminationPattern object containing metadata about the method used to acquire this imaging data.
            quantity: 1

PlanarImagingSpace
^^^^^^^^^^^^^^^
For 2D imaging planes.

.. code-block:: yaml

    groups:
      - neurodata_type_def: PlanarImagingSpace
        neurodata_type_inc: ImagingSpace
        doc: Metadata about the 2-dimensional slice of physical space that imaging data was recorded from.
        datasets:
          - name: pixel_size_in_um
            dtype: float64
            dims:
              - - x, y
            shape:
              - - 2
            doc: The physical dimensions of the pixel in micrometers.
            quantity: "?"
          - name: dimensions_in_pixels
            doc: The number of pixels in the x and y dimensions of the imaging space.
            dtype: uint32
            dims:
              - - x, y
            shape:
              - - 2
            quantity: "?"

VolumetricImagingSpace
^^^^^^^^^^^^^^^^^^^
For 3D imaging volumes.

.. code-block:: yaml

    groups:
      - neurodata_type_def: VolumetricImagingSpace
        neurodata_type_inc: ImagingSpace
        doc: Metadata about the 3-dimensional region of physical space that imaging data was recorded from.
        datasets:
          - name: voxel_size_in_um
            dtype: float64
            dims:
              - - x, y, z
            shape:
              - - 3
            doc: The physical dimensions of the voxel in micrometers.
            quantity: "?"
          - name: dimensions_in_voxels
            doc: The number of voxels in the x, y, and z dimensions of the imaging space.
            dtype: uint32
            dims:
              - - x, y, z
            shape:
              - - 3
            quantity: "?"

Segmentation Components
-------------------

Segmentation
^^^^^^^^^^
Base type for segmentation data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: Segmentation
        neurodata_type_inc: DynamicTable
        doc: Abstract class to contain the results from image segmentation of a specific imaging space.
        attributes:
          - name: description
            dtype: text
            doc: Description of the segmentation method used.
        groups:
          - neurodata_type_inc: SummaryImage
            doc: Summary images that are related to the segmentation, e.g., mean, correlation, maximum projection.
            quantity: "*"

PlanarSegmentation
^^^^^^^^^^^
For 2D segmentation data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: PlanarSegmentation
        neurodata_type_inc: Segmentation
        doc: Results from image segmentation of a specific planar imaging space.
        datasets:
          - name: image_mask
            neurodata_type_inc: VectorData
            dims:
              - - num_roi
                - num_x
                - num_y
            shape:
              - - null
                - null
                - null
            doc: ROI masks for each ROI. Each image mask is the size of the original planar
              imaging space and members of the ROI are finite non-zero.
            quantity: "?"
          - name: pixel_mask_index
            neurodata_type_inc: VectorIndex
            doc: Index into pixel_mask.
            quantity: "?"
          - name: pixel_mask
            neurodata_type_inc: VectorData
            dtype:
              - name: x
                dtype: uint32
                doc: Pixel x-coordinate.
              - name: y
                dtype: uint32
                doc: Pixel y-coordinate.
              - name: weight
                dtype: float32
                doc: Weight of the pixel.
            doc: Pixel masks for each ROI.
            quantity: "?"
        groups:
          - neurodata_type_inc: PlanarImagingSpace
            doc: PlanarImagingSpace object from which this data was generated.

VolumetricSegmentation
^^^^^^^^^^^
For 3D segmentation data.

.. code-block:: yaml

    groups:
      - neurodata_type_def: VolumetricSegmentation
        neurodata_type_inc: Segmentation
        doc: Results from image segmentation of a specific volumetric imaging space.
        datasets:
          - name: volume_mask
            neurodata_type_inc: VectorData
            dims:
              - - num_roi
                - num_x
                - num_y
                - num_z
            shape:
              - - null
                - null
                - null
                - null
            doc: ROI masks for each ROI. Each image mask is the size of the original volumetric
              imaging space and members of the ROI are finite non-zero.
            quantity: "?"
          - name: voxel_mask_index
            neurodata_type_inc: VectorIndex
            doc: Index into voxel_mask.
            quantity: "?"
          - name: voxel_mask
            neurodata_type_inc: VectorData
            dtype:
              - name: x
                dtype: uint32
                doc: Voxel x-coordinate.
              - name: y
                dtype: uint32
                doc: Voxel y-coordinate.
              - name: z
                dtype: uint32
                doc: Voxel z-coordinate.
              - name: weight
                dtype: float32
                doc: Weight of the voxel.
            doc: Voxel masks for each ROI.
            quantity: "?"
        groups:
          - neurodata_type_inc: VolumetricImagingSpace
            doc: VolumetricImagingSpace object from which this data was generated.

SegmentationContainer
^^^^^^^^^^^^^^^^^
Container for multiple segmentations.

.. code-block:: yaml

    groups:
      - neurodata_type_def: SegmentationContainer
        neurodata_type_inc: NWBDataInterface
        default_name: SegmentationContainer
        doc: A container of many Segmentation objects.
        groups:
          - neurodata_type_inc: Segmentation
            doc: Results from image segmentation of a specific imaging space.
            quantity: "+"

SummaryImage
^^^^^^^^^^
Summary images related to segmentation.

.. code-block:: yaml

    groups:
      - neurodata_type_def: SummaryImage
        neurodata_type_inc: NWBContainer
        doc: Summary images that are related to the segmentation, e.g., mean, correlation, maximum projection.
        datasets:
          - name: data
            doc: Summary image data.
            dtype: numeric
            dims:
              - - height
                - width
              - - height
                - width
                - depth
            shape:
              - - null
                - null
              - - null
                - null
                - null
        attributes:
          - name: description
            dtype: text
            doc: Description of the summary image.

MicroscopyResponseSeries
^^^^^^^^^^^^^^^^^^^^
For extracted ROI responses.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MicroscopyResponseSeries
        neurodata_type_inc: TimeSeries
        doc: ROI responses extracted from optical imaging.
        datasets:
          - name: data
            dtype: numeric
            dims:
              - - number_of_frames
                - number_of_rois
            shape:
              - - null
                - null
            doc: Signals from ROIs.
          - name: rois
            neurodata_type_inc: DynamicTableRegion
            doc: DynamicTableRegion referencing segmentation containing more information about the ROIs
              stored in this series.
        links:
          - name: microscopy_series
            doc: Link to a MicroscopySeries object containing the imaging data this response series is derived from.
            target_type: MicroscopySeries

MicroscopyResponseSeriesContainer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Container for multiple response series.

.. code-block:: yaml

    groups:
      - neurodata_type_def: MicroscopyResponseSeriesContainer
        neurodata_type_inc: NWBDataInterface
        default_name: MicroscopyResponseSeriesContainer
        doc: A container of many MicroscopyResponseSeries.
        groups:
          - neurodata_type_inc: MicroscopyResponseSeries
            doc: MicroscopyResponseSeries object(s) containing fluorescence data for a ROI.
            quantity: "+"
