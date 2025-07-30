# ndx-microscopy Extension for NWB

A Neurodata Without Borders (NWB) extension for storing microscopy data and associated metadata in a standardized format. This extension integrates with [ndx-ophys-devices](https://github.com/catalystneuro/ndx-ophys-devices) to provide comprehensive optical component specifications.

## Features

**Comprehensive Neurodata Types**
- Microscope and optical component metadata (integration with [ndx-ophys-devices](https://github.com/catalystneuro/ndx-ophys-devices)):
    - `MicroscopeModel`
    - `Microscope`
    - `MicroscopyRig`
    - `ExcitationSource` / `PulsedExcitationSource`
    - `BandOpticalFilter` / `EdgeOpticalFilter` / 
    - `DichroicMirror` 
    - `Photodetector` 
    - `Indicator`
- Microscopy channel configurations: 
    - `MicroscopyChannel`
- Imaging space definitions: 
    - `PlanarImagingSpace`
    - `VolumetricImagingSpace`
- Illumination pattern classes:
    - `IlluminationPattern`
    - `LineScan`
    - `PlaneAcquisition`
    - `RandomAccessScan`
- Support for 2D and 3D imaging: 
    - `PlanarMicroscopySeries`
    - `VolumetricMicroscopySeries`
    - `MultiPlaneMicroscopyContainer`
    - `MultiChannelMicroscopyContainer`
- ROI/segmentation storage: 
    - `PlanarSegmentation`
    - `VolumetricSegmentation`
    - `SegmentationContainer`
    - `MicroscopyResponseSeries`
    - `MicroscopyResponseSeriesContainer`
- Abstract Neurodata types: `ImagingSpace`, `MicroscopySeries`,`Segmentation`

## Entity Relationship Diagrams

#### Device Components

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', 'primaryBorderColor': '#144E73', 'lineColor': '#D96F32'}}}%%

classDiagram
    direction TB
    
    class DeviceModel{
        <<Device>>
        --------------------------------------
        attributes
        --------------------------------------
        manufacturer : text
        model_number : text, optional
    }
    
    class DeviceInstance{
        <<Device>>
        --------------------------------------
        attributes
        --------------------------------------
        serial_number : text, optional
        --------------------------------------
        links
        --------------------------------------
        model : DeviceModel, optional
    }

    class MicroscopeModel {
        <<DeviceModel>>
    }

    class Microscope {
        <<DeviceInstance>>
        --------------------------------------
        attributes
        --------------------------------------
        technique : text, optional
    }

    class MicroscopyRig {
        <<NWBContainer>>
        --------------------------------------
        attributes
        --------------------------------------
        description : text
        --------------------------------------
        links
        --------------------------------------
        microscope : Microscope
        excitation_source : ExcitationSource, optional
        excitation_filter : OpticalFilter, optional
        dichroic_mirror : DichroicMirror, optional
        photodetector : Photodetector, optional
        emission_filter : OpticalFilter, optional
    }

    class ExcitationSource {
        <<DeviceInstance>>
        --------------------------------------
        attributes
        --------------------------------------
        **illumination_type** : text
        **excitation_wavelength_in_nm** : float
        **excitation_mode** : text
        power_in_W : float, optional
        intensity_in_W_per_m2 : float, optional
        exposure_time_in_s : float, optional
    }

    class PulsedExcitationSource {
        <<ExcitationSource>>
        --------------------------------------
        attributes
        --------------------------------------
        peak_power_in_W : float, optional
        peak_pulse_energy_in_J : float, optional
        pulse_rate_in_Hz : float, optional
    }

    class OpticalFilter {
        <<DeviceInstance>>
        --------------------------------------
        attributes
        --------------------------------------
        **filter_type** : text
    }

    class BandOpticalFilter {
        <<OpticalFilter>>
        --------------------------------------
        attributes
        --------------------------------------
        **center_wavelength_in_nm** : float
        **bandwidth_in_nm** : float
    }

    class EdgeOpticalFilter {
        <<OpticalFilter>>
        --------------------------------------
        attributes
        --------------------------------------
        **cut_wavelength_in_nm** : float
        slope_in_percent_cut_wavelength : float, optional
        slope_starting_transmission_in_percent : float, optional
        slope_ending_transmission_in_percent : float, optional
    }

    class DichroicMirror {
        <<DeviceInstance>>
        --------------------------------------
        attributes
        --------------------------------------
        cut_on_wavelength_in_nm : numeric, optional
        cut_off_wavelength_in_nm : numeric, optional
        reflection_band_in_nm : numeric, optional
        transmission_band_in_nm : numeric, optional
        angle_of_incidence_in_degrees : numeric, optional
    }
    
    class Photodetector {
        <<DeviceInstance>>
        --------------------------------------
        attributes
        --------------------------------------
        **detector_type** : text
        **detected_wavelength_in_nm** : float
        gain : float, optional
        gain_unit : text, optional
    }

    class Indicator {
        <<NWBContainer>>
        --------------------------------------
        attributes
        --------------------------------------
        **label** : text
        description : text, optional
        manufacturer : text, optional
        injection_brain_region : text, optional
        injection_coordinates_in_mm : float[3], optional
    }

    DeviceModel <|-- MicroscopeModel : extends
    DeviceInstance <|-- Microscope : extends

    Microscope o--> MicroscopeModel : links
    MicroscopyRig o--> Microscope : links
    MicroscopyRig o--> ExcitationSource : links
    MicroscopyRig o--> OpticalFilter : links
    MicroscopyRig o--> DichroicMirror : links
    MicroscopyRig o--> Photodetector : links
```

#### Illumination Pattern Components

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', 'primaryBorderColor': '#144E73', 'lineColor': '#D96F32'}}}%%

classDiagram
    direction TB

    class IlluminationPattern {
        <<NWBContainer>>
        --------------------------------------
        attributes
        --------------------------------------
        description : text, optional
    }

    class LineScan {
        <<IlluminationPattern>>
        --------------------------------------
        attributes
        --------------------------------------
        scan_direction : text, optional
        line_rate_in_Hz : float64, optional
        dwell_time_in_s : float64, optional
    }

    class PlaneAcquisition {
        <<IlluminationPattern>>
        --------------------------------------
        attributes
        --------------------------------------
        point_spread_function_in_um : text, optional
        illumination_angle_in_degrees : float64, optional
        plane_rate_in_Hz : float64, optional
    }

    class RandomAccessScan {
        <<IlluminationPattern>>
        --------------------------------------
        attributes
        --------------------------------------
        max_scan_points : numeric, optional
        dwell_time_in_s : float64, optional
        scanning_pattern : text, optional
    }

    class ImagingSpace {
        <<NWBContainer>>
        --------------------------------------
        datasets
        --------------------------------------
        **description** : text
        origin_coordinates : float64[3], optional
        unit : text = "micrometers"
        --------------------------------------
        attributes
        --------------------------------------
        location : text, optional
        reference_frame : text, optional
        orientation : text, optional
        --------------------------------------
        groups
        --------------------------------------
        **illumination_pattern** : IlluminationPattern
    }

    IlluminationPattern <|-- LineScan : extends
    IlluminationPattern <|-- PlaneAcquisition : extends
    IlluminationPattern <|-- RandomAccessScan : extends
    ImagingSpace *-- IlluminationPattern : contains
```

#### Microscopy Series and Imaging Space Components

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', 'primaryBorderColor': '#144E73', 'lineColor': '#D96F32'}}}%%

classDiagram
    direction TB

    class MicroscopyChannel {
        <<NWBContainer>>
        --------------------------------------
        attributes
        --------------------------------------
        **name** : text
        description : text, optional
        **excitation_wavelength_in_nm** : float
        **emission_wavelength_in_nm** : float
        --------------------------------------
        groups
        --------------------------------------
        indicator
    }

    class MicroscopySeries {
        <<TimeSeries>>
        --------------------------------------
        groups
        --------------------------------------
        **microscopy_rig** : MicroscopyRig
        **microscopy_channel** : MicroscopyChannel

    }

    class PlanarMicroscopySeries {
        <<MicroscopySeries>>
        --------------------------------------
        datasets
        --------------------------------------
        **data** : numeric[frames, height, width]
        --------------------------------------
        groups
        --------------------------------------
        **imaging_space** : PlanarImagingSpace
    }

    class VolumetricMicroscopySeries {
        <<MicroscopySeries>>
        --------------------------------------
        datasets
        --------------------------------------
        **data** : numeric[frames, height, width, depths]
        --------------------------------------
        groups
        --------------------------------------
        **imaging_space** : VolumetricImagingSpace
    }

    class MultiPlaneMicroscopyContainer {
        <<NWBDataInterface>>
        --------------------------------------
        groups
        --------------------------------------
        **planar_microscopy_series** : PlanarMicroscopySeries[1..*]
    }

    
    class MultiChannelMicroscopyContainer {
        <<NWBDataInterface>>
        --------------------------------------
        groups
        --------------------------------------
        **microscopy_series** : MicroscopySeries[1..*]
    }

    class ImagingSpace {
        <<NWBContainer>>
        --------------------------------------
        datasets
        --------------------------------------
        **description** : text
        origin_coordinates : float64[3], optional
        unit : text = "micrometers"
        --------------------------------------
        attributes
        --------------------------------------
        location : text, optional
        reference_frame : text, optional
        orientation : text, optional
        --------------------------------------
        groups
        --------------------------------------
        **illumination_pattern** : IlluminationPattern
    }

    class PlanarImagingSpace {
        <<ImagingSpace>>
        --------------------------------------
        datasets
        --------------------------------------
        pixel_size_in_um : float64[2], optional
        dimensions_in_pixels : float64[2], optional 
        --------------------------------------
        methods
        --------------------------------------
        get_FOV_size()
    }

    class VolumetricImagingSpace {
        <<ImagingSpace>>
        --------------------------------------
        datasets
        --------------------------------------
        voxel_size_in_um : float64[3], optional
        dimensions_in_voxels : float64[3], optional 
        --------------------------------------
        methods
        --------------------------------------
        get_FOV_size()
    }

    class MicroscopyRig {
        <<NWBContainer>>
        --------------------------------------
        attributes
        --------------------------------------
        description : text
        --------------------------------------
        links
        --------------------------------------
        microscope : Microscope
        excitation_source : ExcitationSource, optional
        excitation_filter : OpticalFilter, optional
        dichroic_mirror : DichroicMirror, optional
        photodetector : Photodetector, optional
        emission_filter : OpticalFilter, optional
    }

    MicroscopySeries <|-- PlanarMicroscopySeries : extends
    MicroscopySeries <|-- VolumetricMicroscopySeries : extends
    ImagingSpace <|-- PlanarImagingSpace : extends
    ImagingSpace <|-- VolumetricImagingSpace : extends
    
    PlanarMicroscopySeries *-- PlanarImagingSpace : contains
    VolumetricMicroscopySeries *-- VolumetricImagingSpace : contains
    MultiPlaneMicroscopyContainer *-- PlanarMicroscopySeries : contains
    MultiChannelMicroscopyContainer *-- MicroscopySeries : contains
    MicroscopySeries *-- MicroscopyRig : contains
    MicroscopyChannel *-- MicroscopySeries : contains    
    MicroscopyChannel --* Indicator : contains
```

#### Segmentation Components

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', 'primaryBorderColor': '#144E73', 'lineColor': '#D96F32'}}}%%

classDiagram
    direction TB

    class Segmentation {
        <<DynamicTable>>
        --------------------------------------
        attributes
        --------------------------------------
        **description** : text
        --------------------------------------
        groups
        --------------------------------------
        summary_images : SummaryImage[0..*]
    }

    class PlanarSegmentation {
        <<Segmentation>>
        --------------------------------------
        datasets
        --------------------------------------
        image_mask : VectorData[num_roi, num_x, num_y], optional
        pixel_mask_index : VectorIndex, optional
        pixel_mask : VectorData, optional
        --------------------------------------
        groups
        --------------------------------------
        **imaging_space** : PlanarImagingSpace
        --------------------------------------
        methods
        --------------------------------------
        add_roi()
        create_roi_table_region()
        pixel_to_image()
        image_to_pixel()
    }

    class VolumetricSegmentation {
        <<Segmentation>>
        --------------------------------------
        datasets
        --------------------------------------
        volume_mask : VectorData[num_roi, num_x, num_y, num_z], optional
        voxel_mask_index : VectorIndex, optional
        voxel_mask : VectorData, optional
        --------------------------------------
        groups
        --------------------------------------
        **imaging_space** : VolumetricImagingSpace
        --------------------------------------
        methods
        --------------------------------------
        add_roi()
        create_roi_table_region()
        voxel_to_volume()
        volume_to_voxel()
    }

    class SummaryImage {
        <<NWBContainer>>
        --------------------------------------
        datasets
        --------------------------------------
        **data** : numeric[height, width] or numeric[height, width, depth]
        --------------------------------------
        attributes
        --------------------------------------
        **description** : text
    }

    class SegmentationContainer {
        <<NWBDataInterface>>
        --------------------------------------
        groups
        --------------------------------------
        **segmentations** : Segmentation[1..*]
        --------------------------------------
        methods
        --------------------------------------
        add_segmentation()
    }

    class MicroscopyResponseSeries {
        <<TimeSeries>>
        --------------------------------------
        datasets
        --------------------------------------
        **data** : numeric[number_of_frames, number_of_rois]
        **rois** : DynamicTableRegion
        --------------------------------------
        links
        --------------------------------------
        microscopy_saeries : MicroscopySeries, optional
    }

    class MicroscopyResponseSeriesContainer {
        <<NWBDataInterface>>
        --------------------------------------
        groups
        --------------------------------------
        **microscopy_response_series** : MicroscopyResponseSeries[1..*]
    }

    Segmentation <|-- PlanarSegmentation : extends
    Segmentation <|-- VolumetricSegmentation : extends
    SegmentationContainer *-- Segmentation : contains
    Segmentation *-- SummaryImage : contains
    MicroscopyResponseSeries o--> MicroscopySeries : links
    MicroscopyResponseSeriesContainer *-- MicroscopyResponseSeries : contains
    PlanarSegmentation *-- PlanarImagingSpace : contains
    VolumetricSegmentation *-- VolumetricImagingSpace : contains
```

---
This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).

## Installation

```bash
pip install ndx-microscopy
```

## Documentation

For detailed documentation, including API reference and additional examples, please visit our [documentation site](https://ndx-microscopy.readthedocs.io/).


## Contributing

To help ensure a smooth Pull Request (PR) process, please always begin by raising an issue on the main repository so we can openly discuss any problems/additions before taking action.

The main branch of ndx-microscopy is protected; you cannot push to it directly. You must upload your changes by pushing a new branch, then submit your changes to the main branch via a Pull Request. This allows us to conduct automated testing of your contribution, and gives us a space for developers to discuss the contribution and request changes. If you decide to tackle an issue, please make yourself an assignee on the issue to communicate this to the team. Don't worry - this does not commit you to solving this issue. It just lets others know who they should talk to about it.

From your local copy directory, use the following commands.

If you have not already, you will need to clone the repo:
```bash
$ git clone https://github.com/catalystneuro/ndx-microscopy
```

First create a new branch to work on
```bash
$ git checkout -b <new_branch>
```

Make your changes. Add new objects related to optical experiment or add more attributes on the existing ones. To speed up the process, you can write mock function (see _mock.py) that would be used to test the new neurodata type

We will automatically run tests to ensure that your contributions didn't break anything and that they follow our style guide. You can speed up the testing cycle by running these tests locally on your own computer by calling pytest from the top-level directory.
Push your feature branch to origin (i.e. GitHub)

```bash
$ git push origin <new_branch>
```

Once you have tested and finalized your changes, create a pull request (PR) targeting dev as the base branch:
Ensure the PR description clearly describes the problem and solution.
Include the relevant issue number if applicable. TIP: Writing e.g. "fix #613" will automatically close issue #613 when this PR is merged.
Before submitting, please ensure that the code follows the standard coding style of the respective repository.
If you would like help with your contribution, or would like to communicate contributions that are not ready to merge, submit a PR where the title begins with "[WIP]."

Update the CHANGELOG.md regularly to document changes to the extension.

## License

MIT License. See [LICENSE.txt](LICENSE.txt) for details.
