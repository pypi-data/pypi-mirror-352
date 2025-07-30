import warnings
from typing import List, Optional, Tuple

import numpy as np
import pynwb.base
from ndx_ophys_devices import ExcitationSource, OpticalFilter, Photodetector, DichroicMirror, Indicator

from ndx_ophys_devices.testing import (
    mock_ExcitationSource,
    mock_OpticalFilter,
    mock_Photodetector,
    mock_DichroicMirror,
    mock_Indicator,
)

from pynwb.testing.mock.utils import name_generator

import ndx_microscopy


def mock_MicroscopeModel(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a MicroscopeModel type to be used for rapid testing.",
    manufacturer: str = "A fake manufacturer of the mock microscope.",
    model_number: str = "A fake model of the mock microscope.",
) -> ndx_microscopy.MicroscopeModel:
    microscope_model = ndx_microscopy.MicroscopeModel(
        name=name or name_generator("MicroscopeModel"),
        description=description,
        manufacturer=manufacturer,
        model_number=model_number,
    )
    return microscope_model


def mock_Microscope(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a Microscope type to be used for rapid testing.",
    model: ndx_microscopy.MicroscopeModel = None,
    serial_number: str = "A fake serial number of the mock microscope.",
    technique: str = "A fake technique used by the mock microscope.",
) -> ndx_microscopy.Microscope:
    microscope = ndx_microscopy.Microscope(
        name=name or name_generator("Microscope"),
        description=description,
        model=model or mock_MicroscopeModel(),
        serial_number=serial_number,
        technique=technique,
    )
    return microscope


def mock_MicroscopyChannel(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a MicroscopyChannel type to be used for rapid testing.",
    excitation_wavelength_in_nm: Optional[float] = 488.0,
    emission_wavelength_in_nm: Optional[float] = 520.0,
    indicator: Indicator = None,
) -> ndx_microscopy.MicroscopyChannel:
    microscopy_channel = ndx_microscopy.MicroscopyChannel(
        name=name or name_generator("MicroscopyChannel"),
        description=description,
        excitation_wavelength_in_nm=excitation_wavelength_in_nm,
        emission_wavelength_in_nm=emission_wavelength_in_nm,
        indicator=indicator or mock_Indicator(),
    )
    return microscopy_channel


def mock_MicroscopyRig(
    *,
    name: Optional[str] = None,
    description: str = None,
    microscope: ndx_microscopy.Microscope = None,
    excitation_source: ExcitationSource = None,
    excitation_filter: OpticalFilter = None,
    dichroic_mirror: DichroicMirror = None,
    photodetector: Photodetector = None,
    emission_filter: OpticalFilter = None,
) -> ndx_microscopy.MicroscopyRig:
    microscopy_rig = ndx_microscopy.MicroscopyRig(
        name=name or name_generator("MicroscopyRig"),
        description=description or "A mock instance of a MicroscopyRig type to be used for rapid testing.",
        microscope=microscope or mock_Microscope(),
        excitation_source=excitation_source or mock_ExcitationSource(),
        excitation_filter=excitation_filter or mock_OpticalFilter(),
        dichroic_mirror=dichroic_mirror or mock_DichroicMirror(),
        photodetector=photodetector or mock_Photodetector(),
        emission_filter=emission_filter or mock_OpticalFilter(),
    )
    return microscopy_rig


def mock_IlluminationPattern(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of an IlluminationPattern type to be used for rapid testing.",
) -> ndx_microscopy.IlluminationPattern:
    """Base class for describing microscopy imaging modalities."""
    illumination_pattern = ndx_microscopy.IlluminationPattern(
        name=name or name_generator("IlluminationPattern"),
        description=description,
    )
    return illumination_pattern


def mock_LineScan(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a LineScan type to be used for rapid testing.",
    scan_direction: Optional[str] = "horizontal",
    line_rate_in_Hz: Optional[float] = 1000.0,
    dwell_time_in_s: Optional[float] = 1.0e-6,
) -> ndx_microscopy.LineScan:
    """Line scanning method used in microscopy, particularly common in two-photon imaging."""
    line_scan = ndx_microscopy.LineScan(
        name=name or name_generator("LineScan"),
        description=description,
        scan_direction=scan_direction,
        line_rate_in_Hz=line_rate_in_Hz,
        dwell_time_in_s=dwell_time_in_s,
    )
    return line_scan


def mock_PlaneAcquisition(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a PlaneAcquisition type to be used for rapid testing.",
    point_spread_function_in_um: Optional[str] = "32 um ± 1.6 um",
    illumination_angle_in_degrees: Optional[float] = 45.0,
    plane_rate_in_Hz: Optional[float] = 100.0,
) -> ndx_microscopy.PlaneAcquisition:
    """Light sheet method."""
    plane_acquisition = ndx_microscopy.PlaneAcquisition(
        name=name or name_generator("PlaneAcquisition"),
        description=description,
        point_spread_function_in_um=point_spread_function_in_um,
        illumination_angle_in_degrees=illumination_angle_in_degrees,
        plane_rate_in_Hz=plane_rate_in_Hz,
    )
    return plane_acquisition


def mock_RandomAccessScan(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a RandomAccessScan type to be used for rapid testing.",
    max_scan_points: Optional[int] = 1000,
    dwell_time_in_s: Optional[float] = 1.0e-6,
    scanning_pattern: Optional[str] = "spiral",
) -> ndx_microscopy.RandomAccessScan:
    """Random access scanning method for targeted, high-speed imaging of specific regions."""
    random_access_scan = ndx_microscopy.RandomAccessScan(
        name=name or name_generator("RandomAccessScan"),
        description=description,
        max_scan_points=max_scan_points,
        dwell_time_in_s=dwell_time_in_s,
        scanning_pattern=scanning_pattern,
    )
    return random_access_scan


def mock_PlanarImagingSpace(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a PlanarImagingSpace type to be used for rapid testing.",
    origin_coordinates: Tuple[float, float, float] = (-1.2, -0.6, -2),
    pixel_size_in_um: Tuple[float, float] = (20, 20),
    dimensions_in_pixels: Tuple[int, int] = (100, 100),
    location: str = "The location targeted by the mock imaging space.",
    reference_frame: str = "The reference frame of the mock planar imaging space.",
    orientation: str = "The orientation of the mock planar imaging space.",
    illumination_pattern: ndx_microscopy.IlluminationPattern = None,
) -> ndx_microscopy.PlanarImagingSpace:
    planar_imaging_space = ndx_microscopy.PlanarImagingSpace(
        name=name or name_generator("PlanarImagingSpace"),
        description=description,
        origin_coordinates=origin_coordinates,
        pixel_size_in_um=pixel_size_in_um,
        dimensions_in_pixels=dimensions_in_pixels,
        location=location,
        reference_frame=reference_frame,
        orientation=orientation,
        illumination_pattern=illumination_pattern or mock_IlluminationPattern(),
    )
    return planar_imaging_space


def mock_VolumetricImagingSpace(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a VolumetricImagingSpace type to be used for rapid testing.",
    origin_coordinates: Tuple[float, float, float] = (-1.2, -0.6, -2),
    voxel_size_in_um: Tuple[float, float, float] = (20, 20, 50),
    dimensions_in_voxels: Tuple[int, int] = (100, 100, 100),
    location: str = "The location targeted by the mock imaging space.",
    reference_frame: str = "The reference frame of the mock volumetric imaging space.",
    orientation: str = "The orientation of the mock planar imaging space.",
    illumination_pattern: ndx_microscopy.IlluminationPattern = None,
) -> ndx_microscopy.VolumetricImagingSpace:
    volumetric_imaging_space = ndx_microscopy.VolumetricImagingSpace(
        name=name or name_generator("VolumetricImagingSpace"),
        description=description,
        origin_coordinates=origin_coordinates,
        voxel_size_in_um=voxel_size_in_um,
        dimensions_in_voxels=dimensions_in_voxels,
        location=location,
        reference_frame=reference_frame,
        orientation=orientation,
        illumination_pattern=illumination_pattern or mock_IlluminationPattern(),
    )
    return volumetric_imaging_space


def mock_SummaryImage(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a SummaryImage type to be used for rapid testing.",
    image_shape: Tuple[int, int] = (10, 10),
    data: Optional[np.ndarray] = None,
) -> ndx_microscopy.SummaryImage:
    name = name or name_generator("SummaryImage")
    data = data if data is not None else np.ones(image_shape)
    summary_image = ndx_microscopy.SummaryImage(name=name, description=description, data=data)
    return summary_image


def mock_Segmentation(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a Segmentation type to be used for rapid testing.",
    summary_images: Optional[List[ndx_microscopy.SummaryImage]] = None,
) -> ndx_microscopy.Segmentation:
    """Base abstract class with summary images."""
    name = name or name_generator("Segmentation")

    # Create default summary images if none provided
    if summary_images is None:
        mean_image = mock_SummaryImage(name="mean", description="Mean intensity projection")
        max_image = mock_SummaryImage(name="max", description="Maximum intensity projection")
        summary_images = [mean_image, max_image]

    segmentation = ndx_microscopy.Segmentation(name=name, description=description, summary_images=summary_images)

    return segmentation


def mock_PlanarSegmentation(
    *,
    planar_imaging_space: ndx_microscopy.PlanarImagingSpace,
    name: Optional[str] = None,
    description: str = "A mock instance of a PlanarSegmentation type to be used for rapid testing.",
    number_of_rois: int = 5,
    image_shape: Tuple[int, int] = (10, 10),
    summary_images: Optional[List[ndx_microscopy.SummaryImage]] = None,
) -> ndx_microscopy.PlanarSegmentation:
    """2D segmentation with image_mask/pixel_mask."""
    name = name or name_generator("PlanarSegmentation")

    # Create default summary images if none provided
    if summary_images is None:
        mean_image = mock_SummaryImage(name="mean", description="Mean intensity projection", image_shape=image_shape)
        max_image = mock_SummaryImage(name="max", description="Maximum intensity projection", image_shape=image_shape)
        summary_images = [mean_image, max_image]

    planar_segmentation = ndx_microscopy.PlanarSegmentation(
        name=name,
        description=description,
        planar_imaging_space=planar_imaging_space,
        id=list(range(number_of_rois)),
        summary_images=summary_images,
    )

    # Add image masks
    image_masks = list()
    for _ in range(number_of_rois):
        image_masks.append(np.zeros(image_shape, dtype=bool))

    planar_segmentation.add_column(name="image_mask", description="ROI image masks", data=image_masks)

    return planar_segmentation


def mock_VolumetricSegmentation(
    *,
    volumetric_imaging_space: ndx_microscopy.VolumetricImagingSpace,
    name: Optional[str] = None,
    description: str = "A mock instance of a VolumetricSegmentation type to be used for rapid testing.",
    number_of_rois: int = 5,
    volume_shape: Tuple[int, int, int] = (10, 10, 10),
    summary_images: Optional[List[ndx_microscopy.SummaryImage]] = None,
) -> ndx_microscopy.VolumetricSegmentation:
    """3D segmentation with image_mask/voxel_mask."""
    name = name or name_generator("VolumetricSegmentation")

    # Create default summary images if none provided
    if summary_images is None:
        mean_image = mock_SummaryImage(name="mean", description="Mean intensity projection", image_shape=volume_shape)
        max_image = mock_SummaryImage(name="max", description="Maximum intensity projection", image_shape=volume_shape)
        summary_images = [mean_image, max_image]

    volumetric_segmentation = ndx_microscopy.VolumetricSegmentation(
        name=name,
        description=description,
        volumetric_imaging_space=volumetric_imaging_space,
        id=list(range(number_of_rois)),
        summary_images=summary_images,
    )

    # Add image masks
    image_masks = list()
    for _ in range(number_of_rois):
        image_masks.append(np.zeros(volume_shape, dtype=bool))

    volumetric_segmentation.add_column(name="volume_mask", description="ROI image masks", data=image_masks)

    return volumetric_segmentation


def mock_SegmentationContainer(
    *,
    name: Optional[str] = None,
    segmentations: Optional[List[ndx_microscopy.Segmentation]] = None,
) -> ndx_microscopy.SegmentationContainer:
    """Container for multiple segmentations."""
    name = name or name_generator("SegmentationContainer")

    # Create default segmentations if none provided
    if segmentations is None:
        planar_imaging_space = mock_PlanarImagingSpace()
        volumetric_imaging_space = mock_VolumetricImagingSpace()
        segmentations = [
            mock_PlanarSegmentation(planar_imaging_space=planar_imaging_space),
            mock_VolumetricSegmentation(volumetric_imaging_space=volumetric_imaging_space),
        ]

    container = ndx_microscopy.SegmentationContainer(name=name, segmentations=segmentations)

    return container


def mock_PlanarMicroscopySeries(
    *,
    microscopy_rig: ndx_microscopy.MicroscopyRig,
    planar_imaging_space: ndx_microscopy.PlanarImagingSpace,
    microscopy_channel: ndx_microscopy.MicroscopyChannel,
    name: Optional[str] = None,
    description: str = "A mock instance of a PlanarMicroscopySeries type to be used for rapid testing.",
    data: Optional[np.ndarray] = None,
    unit: str = "a.u.",
    conversion: float = 1.0,
    offset: float = 0.0,
    starting_time: Optional[float] = None,
    rate: Optional[float] = None,
    timestamps: Optional[np.ndarray] = None,
) -> ndx_microscopy.PlanarMicroscopySeries:
    series_name = name or name_generator("PlanarMicroscopySeries")
    series_data = data if data is not None else np.ones(shape=(15, 5, 5))

    if timestamps is None:
        series_starting_time = starting_time or 0.0
        series_rate = rate or 10.0
        series_timestamps = None
    else:
        if starting_time is not None or rate is not None:
            warnings.warn(
                message=(
                    "Timestamps were provided in addition to either rate or starting_time! "
                    "Please specify only timestamps, or both starting_time and rate. Timestamps will take precedence."
                ),
                stacklevel=2,
            )

        series_starting_time = None
        series_rate = None
        series_timestamps = timestamps

    planar_microscopy_series = ndx_microscopy.PlanarMicroscopySeries(
        name=series_name,
        description=description,
        microscopy_rig=microscopy_rig,
        microscopy_channel=microscopy_channel,
        planar_imaging_space=planar_imaging_space,
        data=series_data,
        unit=unit,
        conversion=conversion,
        offset=offset,
        starting_time=series_starting_time,
        rate=series_rate,
        timestamps=series_timestamps,
    )
    return planar_microscopy_series


def mock_MultiPlaneMicroscopyContainer(
    *,
    planar_microscopy_series: List[ndx_microscopy.PlanarMicroscopySeries],
    name: Optional[str] = None,
) -> ndx_microscopy.MultiPlaneMicroscopyContainer:
    container_name = name or name_generator("MultiPlaneMicroscopyContainer")

    multi_plane_microscopy_container = ndx_microscopy.MultiPlaneMicroscopyContainer(
        name=container_name, planar_microscopy_series=planar_microscopy_series
    )

    return multi_plane_microscopy_container


def mock_MultiChannelMicroscopyContainer(
    *,
    microscopy_series: List[ndx_microscopy.MicroscopySeries],
    name: Optional[str] = None,
) -> ndx_microscopy.MultiChannelMicroscopyContainer:
    container_name = name or name_generator("MultiChannelMicroscopyContainer")

    multi_channel_microscopy_container = ndx_microscopy.MultiChannelMicroscopyContainer(
        name=container_name, microscopy_series=microscopy_series
    )

    return multi_channel_microscopy_container


def mock_VolumetricMicroscopySeries(
    *,
    microscopy_rig: ndx_microscopy.MicroscopyRig,
    volumetric_imaging_space: ndx_microscopy.VolumetricImagingSpace,
    microscopy_channel: ndx_microscopy.MicroscopyChannel,
    name: Optional[str] = None,
    description: str = "A mock instance of a VolumetricMicroscopySeries type to be used for rapid testing.",
    data: Optional[np.ndarray] = None,
    unit: str = "a.u.",
    conversion: float = 1.0,
    offset: float = 0.0,
    starting_time: Optional[float] = None,
    rate: Optional[float] = None,
    timestamps: Optional[np.ndarray] = None,
) -> ndx_microscopy.VolumetricMicroscopySeries:
    series_name = name or name_generator("VolumetricMicroscopySeries")
    series_data = data if data is not None else np.ones(shape=(5, 5, 5, 3))

    if timestamps is None:
        series_starting_time = starting_time or 0.0
        series_rate = rate or 10.0
        series_timestamps = None
    else:
        if starting_time is not None or rate is not None:
            warnings.warn(
                message=(
                    "Timestamps were provided in addition to either rate or starting_time! "
                    "Please specify only timestamps, or both starting_time and rate. Timestamps will take precedence."
                ),
                stacklevel=2,
            )

        series_starting_time = None
        series_rate = None
        series_timestamps = timestamps

    volumetric_microscopy_series = ndx_microscopy.VolumetricMicroscopySeries(
        name=series_name,
        description=description,
        microscopy_channel=microscopy_channel,
        microscopy_rig=microscopy_rig,
        volumetric_imaging_space=volumetric_imaging_space,
        data=series_data,
        unit=unit,
        conversion=conversion,
        offset=offset,
        starting_time=series_starting_time,
        rate=series_rate,
        timestamps=series_timestamps,
    )
    return volumetric_microscopy_series


def mock_MicroscopyResponseSeries(
    *,
    rois: pynwb.core.DynamicTableRegion,
    name: Optional[str] = None,
    description: str = "A mock instance of a MicroscopyResponseSeries type to be used for rapid testing.",
    data: Optional[np.ndarray] = None,
    unit: str = "a.u.",
    conversion: float = 1.0,
    offset: float = 0.0,
    starting_time: Optional[float] = None,
    rate: Optional[float] = None,
    timestamps: Optional[np.ndarray] = None,
    microscopy_series: Optional[ndx_microscopy.MicroscopyResponseSeries] = None,
) -> ndx_microscopy.MicroscopyResponseSeries:
    series_name = name or name_generator("MicroscopyResponseSeries")

    number_of_frames = 100
    number_of_rois = len(rois.data)
    series_data = data if data is not None else np.ones(shape=(number_of_frames, number_of_rois))

    if timestamps is None:
        series_starting_time = starting_time or 0.0
        series_rate = rate or 10.0
        series_timestamps = None
    else:
        if starting_time is not None or rate is not None:
            warnings.warn(
                message=(
                    "Timestamps were provided in addition to either rate or starting_time! "
                    "Please specify only timestamps, or both starting_time and rate. Timestamps will take precedence."
                ),
                stacklevel=2,
            )

        series_starting_time = None
        series_rate = None
        series_timestamps = timestamps

    microscopy_response_series = ndx_microscopy.MicroscopyResponseSeries(
        name=series_name,
        description=description,
        rois=rois,
        data=series_data,
        unit=unit,
        conversion=conversion,
        offset=offset,
        starting_time=series_starting_time,
        rate=series_rate,
        timestamps=series_timestamps,
        microscopy_series=microscopy_series,
    )

    return microscopy_response_series


def mock_MicroscopyResponseSeriesContainer(
    *,
    microscopy_response_series: List[ndx_microscopy.MicroscopyResponseSeries],
    name: Optional[str] = None,
) -> ndx_microscopy.MicroscopyResponseSeriesContainer:
    container_name = name or name_generator("MicroscopyResponseSeriesContainer")

    microscopy_response_series_container = ndx_microscopy.MicroscopyResponseSeriesContainer(
        name=container_name, microscopy_response_series=microscopy_response_series
    )

    return microscopy_response_series_container
