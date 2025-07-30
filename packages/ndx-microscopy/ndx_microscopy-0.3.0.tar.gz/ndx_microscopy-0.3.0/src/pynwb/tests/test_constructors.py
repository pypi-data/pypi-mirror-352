"""Test in-memory Python API constructors for the ndx-microscopy extension."""

import pytest

from ndx_microscopy.testing import (
    mock_MicroscopyRig,
    mock_MicroscopeModel,
    mock_Microscope,
    mock_MicroscopyChannel,
    mock_Segmentation,
    mock_PlanarSegmentation,
    mock_VolumetricSegmentation,
    mock_SegmentationContainer,
    mock_PlanarImagingSpace,
    mock_PlanarMicroscopySeries,
    mock_MultiPlaneMicroscopyContainer,
    mock_MultiChannelMicroscopyContainer,
    mock_VolumetricImagingSpace,
    mock_VolumetricMicroscopySeries,
    mock_MicroscopyResponseSeries,
    mock_MicroscopyResponseSeriesContainer,
    mock_IlluminationPattern,
    mock_LineScan,
    mock_PlaneAcquisition,
    mock_RandomAccessScan,
)

from ndx_microscopy import (
    Segmentation,
    PlanarSegmentation,
    VolumetricSegmentation,
    PlanarImagingSpace,
    VolumetricImagingSpace,
    IlluminationPattern,
    LineScan,
    PlaneAcquisition,
    RandomAccessScan,
)


def test_constructor_microscope():
    microscope = mock_Microscope()
    assert microscope.description == "A mock instance of a Microscope type to be used for rapid testing."


def test_constructor_microscope_model():
    microscope_model = mock_MicroscopeModel()
    assert microscope_model.description == "A mock instance of a MicroscopeModel type to be used for rapid testing."


def test_constructor_microscopy_channel():
    microscopy_channel = mock_MicroscopyChannel()
    assert microscopy_channel.description == "A mock instance of a MicroscopyChannel type to be used for rapid testing."


def test_constructor_microscopy_rig():
    microscopy_rig = mock_MicroscopyRig()
    assert microscopy_rig.description == "A mock instance of a MicroscopyRig type to be used for rapid testing."


def test_constructor_illumination_pattern():
    """Test constructor for base IlluminationPattern class."""
    illumination_pattern = mock_IlluminationPattern()
    assert (
        illumination_pattern.description
        == "A mock instance of an IlluminationPattern type to be used for rapid testing."
    )
    assert isinstance(illumination_pattern, IlluminationPattern)


def test_constructor_line_scan():
    """Test constructor for LineScan class."""
    line_scan = mock_LineScan()
    assert line_scan.description == "A mock instance of a LineScan type to be used for rapid testing."
    assert line_scan.scan_direction == "horizontal"
    assert line_scan.line_rate_in_Hz == 1000.0
    assert line_scan.dwell_time_in_s == 1e-6
    assert isinstance(line_scan, LineScan)
    assert isinstance(line_scan, IlluminationPattern)


def test_constructor_plane_acquisition():
    """Test constructor for PlaneAcquisition class."""
    plane_acquisition = mock_PlaneAcquisition()
    assert plane_acquisition.description == "A mock instance of a PlaneAcquisition type to be used for rapid testing."
    assert plane_acquisition.point_spread_function_in_um == "32 um ± 1.6 um"
    assert plane_acquisition.illumination_angle_in_degrees == 45.0
    assert plane_acquisition.plane_rate_in_Hz == 100.0
    assert isinstance(plane_acquisition, PlaneAcquisition)
    assert isinstance(plane_acquisition, IlluminationPattern)  # Test inheritance


def test_constructor_random_access_scan():
    """Test constructor for RandomAccessScan class."""
    random_access_scan = mock_RandomAccessScan()
    assert random_access_scan.description == "A mock instance of a RandomAccessScan type to be used for rapid testing."
    assert random_access_scan.max_scan_points == 1000
    assert random_access_scan.dwell_time_in_s == 1.0e-6
    assert random_access_scan.scanning_pattern == "spiral"
    assert isinstance(random_access_scan, RandomAccessScan)
    assert isinstance(random_access_scan, IlluminationPattern)  # Test inheritance


def test_constructor_planar_imaging_space():
    planar_imaging_space = mock_PlanarImagingSpace()
    assert (
        planar_imaging_space.description == "A mock instance of a PlanarImagingSpace type to be used for rapid testing."
    )
    assert isinstance(planar_imaging_space, PlanarImagingSpace)


def test_constructor_volumetric_imaging_space():
    volumetric_imaging_space = mock_VolumetricImagingSpace()
    assert (
        volumetric_imaging_space.description
        == "A mock instance of a VolumetricImagingSpace type to be used for rapid testing."
    )
    assert isinstance(volumetric_imaging_space, VolumetricImagingSpace)


def test_constructor_segmentation():
    """Test constructor for base Segmentation class."""
    segmentation = mock_Segmentation()
    assert segmentation.description == "A mock instance of a Segmentation type to be used for rapid testing."
    assert len(segmentation.summary_images) == 2
    assert "mean" in segmentation.summary_images
    assert "max" in segmentation.summary_images
    assert isinstance(segmentation, Segmentation)


def test_constructor_planar_segmentation():
    """Test constructor for PlanarSegmentation class."""
    planar_imaging_space = mock_PlanarImagingSpace()
    segmentation = mock_PlanarSegmentation(planar_imaging_space=planar_imaging_space)
    assert segmentation.description == "A mock instance of a PlanarSegmentation type to be used for rapid testing."
    assert len(segmentation.id) == 5  # Default number_of_rois
    assert "image_mask" in segmentation.colnames
    assert isinstance(segmentation.planar_imaging_space, PlanarImagingSpace)
    assert isinstance(segmentation, PlanarSegmentation)
    assert isinstance(segmentation, Segmentation)  # Test inheritance


def test_constructor_volumetric_segmentation():
    """Test constructor for VolumetricSegmentation class."""
    volumetric_imaging_space = mock_VolumetricImagingSpace()
    segmentation = mock_VolumetricSegmentation(volumetric_imaging_space=volumetric_imaging_space)
    assert segmentation.description == "A mock instance of a VolumetricSegmentation type to be used for rapid testing."
    assert len(segmentation.id) == 5  # Default number_of_rois
    assert "volume_mask" in segmentation.colnames
    assert isinstance(segmentation.volumetric_imaging_space, VolumetricImagingSpace)
    assert isinstance(segmentation, VolumetricSegmentation)
    assert isinstance(segmentation, Segmentation)  # Test inheritance


def test_constructor_segmentation_container():
    """Test constructor for SegmentationContainer class."""
    container = mock_SegmentationContainer()
    assert len(container.segmentations) == 2  # Default includes both planar and volumetric
    segmentation_names = [seg_name for seg_name in container.segmentations]
    assert isinstance(container.segmentations[segmentation_names[0]], PlanarSegmentation)
    assert isinstance(container.segmentations[segmentation_names[1]], VolumetricSegmentation)


def test_constructor_planar_microscopy_series():
    microscopy_rig = mock_MicroscopyRig()
    microscopy_channel = mock_MicroscopyChannel()
    planar_imaging_space = mock_PlanarImagingSpace()

    planar_microscopy_series = mock_PlanarMicroscopySeries(
        microscopy_rig=microscopy_rig,
        microscopy_channel=microscopy_channel,
        planar_imaging_space=planar_imaging_space,
    )
    assert (
        planar_microscopy_series.description
        == "A mock instance of a PlanarMicroscopySeries type to be used for rapid testing."
    )


def test_constructor_multi_plane_microscopy_container():

    microscopy_rig = mock_MicroscopyRig()
    microscopy_channel = mock_MicroscopyChannel()
    planar_imaging_space = mock_PlanarImagingSpace()

    planar_microscopy_series = mock_PlanarMicroscopySeries(
        microscopy_rig=microscopy_rig,
        microscopy_channel=microscopy_channel,
        planar_imaging_space=planar_imaging_space,
    )

    multi_plane_microscopy_container = mock_MultiPlaneMicroscopyContainer(
        planar_microscopy_series=[planar_microscopy_series]
    )
    assert multi_plane_microscopy_container.name == "MultiPlaneMicroscopyContainer"


def test_constructor_multi_channel_microscopy_container():

    microscopy_rig = mock_MicroscopyRig()
    microscopy_channel = mock_MicroscopyChannel()
    planar_imaging_space = mock_PlanarImagingSpace()
    planar_microscopy_series = mock_PlanarMicroscopySeries(
        microscopy_rig=microscopy_rig,
        microscopy_channel=microscopy_channel,
        planar_imaging_space=planar_imaging_space,
    )

    multi_channel_microscopy_container = mock_MultiChannelMicroscopyContainer(
        microscopy_series=[planar_microscopy_series]
    )
    assert multi_channel_microscopy_container.name == "MultiChannelMicroscopyContainer"


def test_constructor_volumetric_microscopy_series():
    microscopy_rig = mock_MicroscopyRig()
    microscopy_channel = mock_MicroscopyChannel()
    volumetric_imaging_space = mock_VolumetricImagingSpace()

    volumetric_microscopy_series = mock_VolumetricMicroscopySeries(
        microscopy_rig=microscopy_rig,
        microscopy_channel=microscopy_channel,
        volumetric_imaging_space=volumetric_imaging_space,
    )
    assert (
        volumetric_microscopy_series.description
        == "A mock instance of a VolumetricMicroscopySeries type to be used for rapid testing."
    )


def test_constructor_microscopy_response_series():
    number_of_rois = 10
    planar_imaging_space = mock_PlanarImagingSpace()
    segmentation = mock_PlanarSegmentation(planar_imaging_space=planar_imaging_space, number_of_rois=number_of_rois)

    rois = segmentation.create_roi_table_region(
        description="test region",
        region=[x for x in range(number_of_rois)],
    )

    microscopy_response_series = mock_MicroscopyResponseSeries(rois=rois)
    assert (
        microscopy_response_series.description
        == "A mock instance of a MicroscopyResponseSeries type to be used for rapid testing."
    )


def test_constructor_microscopy_response_series_with_microscopy_series():

    microscopy_rig = mock_MicroscopyRig()
    microscopy_channel = mock_MicroscopyChannel()
    number_of_rois = 10
    planar_imaging_space = mock_PlanarImagingSpace()
    microscopy_series = mock_PlanarMicroscopySeries(
        microscopy_channel=microscopy_channel,
        microscopy_rig=microscopy_rig,
        planar_imaging_space=planar_imaging_space,
    )
    segmentation = mock_PlanarSegmentation(planar_imaging_space=planar_imaging_space, number_of_rois=number_of_rois)
    rois = segmentation.create_roi_table_region(
        description="test region",
        region=[x for x in range(number_of_rois)],
    )

    microscopy_response_series = mock_MicroscopyResponseSeries(rois=rois, microscopy_series=microscopy_series)
    assert (
        microscopy_response_series.description
        == "A mock instance of a MicroscopyResponseSeries type to be used for rapid testing."
    )


def test_constructor_microscopy_response_series_container():
    number_of_rois = 10
    planar_imaging_space = mock_PlanarImagingSpace()
    segmentation = mock_PlanarSegmentation(planar_imaging_space=planar_imaging_space, number_of_rois=number_of_rois)

    rois = segmentation.create_roi_table_region(
        description="test region",
        region=[x for x in range(number_of_rois)],
    )

    microscopy_response_series = mock_MicroscopyResponseSeries(rois=rois)

    microscopy_response_series_container = mock_MicroscopyResponseSeriesContainer(
        microscopy_response_series=[microscopy_response_series]
    )
    assert microscopy_response_series_container.name == "MicroscopyResponseSeriesContainer"


if __name__ == "__main__":
    pytest.main([__file__])
