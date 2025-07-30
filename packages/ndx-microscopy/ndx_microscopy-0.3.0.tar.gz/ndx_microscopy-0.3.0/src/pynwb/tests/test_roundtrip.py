"""Test roundtrip (write and read back) of the Python API for the ndx-microscopy extension."""

from datetime import datetime

from pytz import UTC
import pytest
from pynwb.testing import TestCase as pynwb_TestCase
from pynwb.testing.mock.file import mock_NWBFile

import pynwb
from ndx_ophys_devices.testing import (
    mock_ExcitationSource,
    mock_Photodetector,
    mock_OpticalFilter,
    mock_DichroicMirror,
    mock_ExcitationSourceModel,
    mock_PhotodetectorModel,
    mock_OpticalFilterModel,
    mock_DichroicMirrorModel,
)

from ndx_microscopy.testing import (
    mock_MicroscopyRig,
    mock_Microscope,
    mock_MicroscopeModel,
    mock_MicroscopyChannel,
    mock_PlanarSegmentation,
    mock_SegmentationContainer,
    mock_PlanarImagingSpace,
    mock_VolumetricImagingSpace,
    mock_PlanarMicroscopySeries,
    mock_MultiPlaneMicroscopyContainer,
    mock_MultiChannelMicroscopyContainer,
    mock_VolumetricMicroscopySeries,
    mock_MicroscopyResponseSeries,
)

from ndx_microscopy import MicroscopyResponseSeriesContainer


class TestPlanarMicroscopySeriesSimpleRoundtrip(pynwb_TestCase):
    """Simple roundtrip test for PlanarMicroscopySeries."""

    def setUp(self):
        self.nwbfile_path = "test_planar_microscopy_series_roundtrip.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        nwbfile = mock_NWBFile(session_start_time=datetime(2000, 1, 1, tzinfo=UTC))

        microscope_model = mock_MicroscopeModel(name="MicroscopeModel")
        nwbfile.add_device(devices=microscope_model)
        microscope = mock_Microscope(name="Microscope", model=microscope_model)
        nwbfile.add_device(devices=microscope)

        excitation_source_model = mock_ExcitationSourceModel(name="ExcitationSourceModel")
        nwbfile.add_device(devices=excitation_source_model)
        excitation_source = mock_ExcitationSource(model=excitation_source_model)
        nwbfile.add_device(devices=excitation_source)

        excitation_filter_model = mock_OpticalFilterModel(name="OpticalFilterModel")
        nwbfile.add_device(devices=excitation_filter_model)
        excitation_filter = mock_OpticalFilter(model=excitation_filter_model)
        nwbfile.add_device(devices=excitation_filter)

        dichroic_mirror_model = mock_DichroicMirrorModel(name="DichroicMirrorModel")
        nwbfile.add_device(devices=dichroic_mirror_model)
        dichroic_mirror = mock_DichroicMirror(model=dichroic_mirror_model)
        nwbfile.add_device(devices=dichroic_mirror)

        photodetector_model = mock_PhotodetectorModel(name="PhotodetectorModel")
        nwbfile.add_device(devices=photodetector_model)
        photodetector = mock_Photodetector(model=photodetector_model)
        nwbfile.add_device(devices=photodetector)

        emission_filter_model = mock_OpticalFilterModel(name="EmissionFilterModel")
        nwbfile.add_device(devices=emission_filter_model)
        emission_filter = mock_OpticalFilter(model=emission_filter_model)
        nwbfile.add_device(devices=emission_filter)

        microscopy_rig = mock_MicroscopyRig(
            name="MicroscopyRig",
            microscope=microscope,
            excitation_source=excitation_source,
            excitation_filter=excitation_filter,
            emission_filter=emission_filter,
            photodetector=photodetector,
            dichroic_mirror=dichroic_mirror,
        )

        planar_imaging_space = mock_PlanarImagingSpace(name="PlanarImagingSpace")

        planar_microscopy_series = mock_PlanarMicroscopySeries(
            name="PlanarMicroscopySeries",
            microscopy_rig=microscopy_rig,
            microscopy_channel=mock_MicroscopyChannel(name="MicroscopyChannel"),
            planar_imaging_space=planar_imaging_space,
        )
        nwbfile.add_acquisition(planar_microscopy_series)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
            io.write(nwbfile)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            self.assertContainerEqual(microscope, read_nwbfile.devices["Microscope"])

            self.assertContainerEqual(planar_microscopy_series, read_nwbfile.acquisition["PlanarMicroscopySeries"])


class TestMicroscopyRigWithUntrackedDevice(pynwb_TestCase):
    """Test that creating an MicroscopyRig with a device that hasn't been added to the NWBFile raises an error."""

    def setUp(self):
        self.nwbfile_path = "test_microscopy_rig_without_device.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        from hdmf.build.errors import OrphanContainerBuildError

        nwbfile = mock_NWBFile(session_start_time=datetime(2000, 1, 1, tzinfo=UTC))

        microscope_model = mock_MicroscopeModel(name="MicroscopeModel")
        nwbfile.add_device(devices=microscope_model)
        microscope = mock_Microscope(name="Microscope", model=microscope_model)
        # nwbfile.add_device(devices=microscope) Skipping this line to simulate an untracked device

        excitation_source_model = mock_ExcitationSourceModel(name="ExcitationSourceModel")
        nwbfile.add_device(devices=excitation_source_model)
        excitation_source = mock_ExcitationSource(model=excitation_source_model)
        nwbfile.add_device(devices=excitation_source)

        excitation_filter_model = mock_OpticalFilterModel(name="OpticalFilterModel")
        nwbfile.add_device(devices=excitation_filter_model)
        excitation_filter = mock_OpticalFilter(model=excitation_filter_model)
        nwbfile.add_device(devices=excitation_filter)

        dichroic_mirror_model = mock_DichroicMirrorModel(name="DichroicMirrorModel")
        nwbfile.add_device(devices=dichroic_mirror_model)
        dichroic_mirror = mock_DichroicMirror(model=dichroic_mirror_model)
        nwbfile.add_device(devices=dichroic_mirror)

        photodetector_model = mock_PhotodetectorModel(name="PhotodetectorModel")
        nwbfile.add_device(devices=photodetector_model)
        photodetector = mock_Photodetector(model=photodetector_model)
        nwbfile.add_device(devices=photodetector)

        emission_filter_model = mock_OpticalFilterModel(name="EmissionFilterModel")
        nwbfile.add_device(devices=emission_filter_model)
        emission_filter = mock_OpticalFilter(model=emission_filter_model)
        nwbfile.add_device(devices=emission_filter)

        microscopy_rig = mock_MicroscopyRig(
            name="MicroscopyRig",
            microscope=microscope,
            excitation_source=excitation_source,
            excitation_filter=excitation_filter,
            emission_filter=emission_filter,
            photodetector=photodetector,
            dichroic_mirror=dichroic_mirror,
        )

        # Create imaging space
        planar_imaging_space = mock_PlanarImagingSpace(name="PlanarImagingSpace")

        planar_microscopy_series = mock_PlanarMicroscopySeries(
            name="PlanarMicroscopySeries",
            microscopy_rig=microscopy_rig,
            microscopy_channel=mock_MicroscopyChannel(name="MicroscopyChannel"),
            planar_imaging_space=planar_imaging_space,
        )
        nwbfile.add_acquisition(planar_microscopy_series)

        with pytest.raises(OrphanContainerBuildError):
            with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
                io.write(nwbfile)


class TestVolumetricMicroscopySeriesSimpleRoundtrip(pynwb_TestCase):
    """Simple roundtrip test for VolumetricMicroscopySeries."""

    def setUp(self):
        self.nwbfile_path = "test_volumetric_microscopy_series_roundtrip.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        nwbfile = mock_NWBFile(session_start_time=datetime(2000, 1, 1, tzinfo=UTC))

        microscope_model = mock_MicroscopeModel(name="MicroscopeModel")
        nwbfile.add_device(devices=microscope_model)
        microscope = mock_Microscope(name="Microscope", model=microscope_model)
        nwbfile.add_device(devices=microscope)

        excitation_source_model = mock_ExcitationSourceModel(name="ExcitationSourceModel")
        nwbfile.add_device(devices=excitation_source_model)
        excitation_source = mock_ExcitationSource(model=excitation_source_model)
        nwbfile.add_device(devices=excitation_source)

        excitation_filter_model = mock_OpticalFilterModel(name="OpticalFilterModel")
        nwbfile.add_device(devices=excitation_filter_model)
        excitation_filter = mock_OpticalFilter(model=excitation_filter_model)
        nwbfile.add_device(devices=excitation_filter)

        dichroic_mirror_model = mock_DichroicMirrorModel(name="DichroicMirrorModel")
        nwbfile.add_device(devices=dichroic_mirror_model)
        dichroic_mirror = mock_DichroicMirror(model=dichroic_mirror_model)
        nwbfile.add_device(devices=dichroic_mirror)

        photodetector_model = mock_PhotodetectorModel(name="PhotodetectorModel")
        nwbfile.add_device(devices=photodetector_model)
        photodetector = mock_Photodetector(model=photodetector_model)
        nwbfile.add_device(devices=photodetector)

        emission_filter_model = mock_OpticalFilterModel(name="EmissionFilterModel")
        nwbfile.add_device(devices=emission_filter_model)
        emission_filter = mock_OpticalFilter(model=emission_filter_model)
        nwbfile.add_device(devices=emission_filter)

        microscopy_rig = mock_MicroscopyRig(
            name="MicroscopyRig",
            microscope=microscope,
            excitation_source=excitation_source,
            excitation_filter=excitation_filter,
            emission_filter=emission_filter,
            photodetector=photodetector,
            dichroic_mirror=dichroic_mirror,
        )

        volumetric_imaging_space = mock_VolumetricImagingSpace(name="VolumetricImagingSpace")

        volumetric_microscopy_series = mock_VolumetricMicroscopySeries(
            name="VolumetricMicroscopySeries",
            microscopy_rig=microscopy_rig,
            microscopy_channel=mock_MicroscopyChannel(name="MicroscopyChannel"),
            volumetric_imaging_space=volumetric_imaging_space,
        )
        nwbfile.add_acquisition(volumetric_microscopy_series)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
            io.write(nwbfile)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            self.assertContainerEqual(microscope, read_nwbfile.devices["Microscope"])

            self.assertContainerEqual(
                volumetric_microscopy_series, read_nwbfile.acquisition["VolumetricMicroscopySeries"]
            )


class TestMultiPlaneMicroscopyContainerSimpleRoundtrip(pynwb_TestCase):
    """Simple roundtrip test for MultiPlaneMicroscopyContainer."""

    def setUp(self):
        self.nwbfile_path = "test_multi_plane_microscopy_container_roundtrip.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        nwbfile = mock_NWBFile(session_start_time=datetime(2000, 1, 1, tzinfo=UTC))

        microscope_model = mock_MicroscopeModel(name="MicroscopeModel")
        nwbfile.add_device(devices=microscope_model)
        microscope = mock_Microscope(name="Microscope", model=microscope_model)
        nwbfile.add_device(devices=microscope)

        excitation_source_model = mock_ExcitationSourceModel(name="ExcitationSourceModel")
        nwbfile.add_device(devices=excitation_source_model)
        excitation_source = mock_ExcitationSource(model=excitation_source_model)
        nwbfile.add_device(devices=excitation_source)

        excitation_filter_model = mock_OpticalFilterModel(name="OpticalFilterModel")
        nwbfile.add_device(devices=excitation_filter_model)
        excitation_filter = mock_OpticalFilter(model=excitation_filter_model)
        nwbfile.add_device(devices=excitation_filter)

        dichroic_mirror_model = mock_DichroicMirrorModel(name="DichroicMirrorModel")
        nwbfile.add_device(devices=dichroic_mirror_model)
        dichroic_mirror = mock_DichroicMirror(model=dichroic_mirror_model)
        nwbfile.add_device(devices=dichroic_mirror)

        photodetector_model = mock_PhotodetectorModel(name="PhotodetectorModel")
        nwbfile.add_device(devices=photodetector_model)
        photodetector = mock_Photodetector(model=photodetector_model)
        nwbfile.add_device(devices=photodetector)

        emission_filter_model = mock_OpticalFilterModel(name="EmissionFilterModel")
        nwbfile.add_device(devices=emission_filter_model)
        emission_filter = mock_OpticalFilter(model=emission_filter_model)
        nwbfile.add_device(devices=emission_filter)

        microscopy_rig = mock_MicroscopyRig(
            name="MicroscopyRig",
            microscope=microscope,
            excitation_source=excitation_source,
            excitation_filter=excitation_filter,
            emission_filter=emission_filter,
            photodetector=photodetector,
            dichroic_mirror=dichroic_mirror,
        )

        planar_imaging_space_1 = mock_PlanarImagingSpace(
            name="PlanarImagingSpace_1", origin_coordinates=[0.0, 0.0, 0.0]
        )
        planar_imaging_space_2 = mock_PlanarImagingSpace(
            name="PlanarImagingSpace_2", origin_coordinates=[0.0, 0.0, 1.0]
        )

        microscopy_channel = mock_MicroscopyChannel(name="MicroscopyChannel")

        planar_microscopy_series_1 = mock_PlanarMicroscopySeries(
            name="PlanarMicroscopySeries_1",
            microscopy_rig=microscopy_rig,
            microscopy_channel=microscopy_channel,
            planar_imaging_space=planar_imaging_space_1,
        )

        planar_microscopy_series_2 = mock_PlanarMicroscopySeries(
            name="PlanarMicroscopySeries_2",
            microscopy_rig=microscopy_rig,
            microscopy_channel=microscopy_channel,
            planar_imaging_space=planar_imaging_space_2,
        )

        multi_plane_microscopy_container = mock_MultiPlaneMicroscopyContainer(
            name="MultiPlaneMicroscopyContainer",
            planar_microscopy_series=[planar_microscopy_series_1, planar_microscopy_series_2],
        )

        nwbfile.add_acquisition(multi_plane_microscopy_container)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
            io.write(nwbfile)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            self.assertContainerEqual(microscope, read_nwbfile.devices["Microscope"])

            self.assertContainerEqual(
                multi_plane_microscopy_container, read_nwbfile.acquisition["MultiPlaneMicroscopyContainer"]
            )


class TestMultiChannelMicroscopyContainerSimpleRoundtrip(pynwb_TestCase):
    """Simple roundtrip test for MultiChannelMicroscopyContainer."""

    def setUp(self):
        self.nwbfile_path = "test_multi_channel_microscopy_container_roundtrip.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        nwbfile = mock_NWBFile(session_start_time=datetime(2000, 1, 1, tzinfo=UTC))

        microscope_model = mock_MicroscopeModel(name="MicroscopeModel")
        nwbfile.add_device(devices=microscope_model)
        microscope = mock_Microscope(name="Microscope", model=microscope_model)
        nwbfile.add_device(devices=microscope)

        excitation_source_model = mock_ExcitationSourceModel(name="ExcitationSourceModel")
        nwbfile.add_device(devices=excitation_source_model)
        excitation_source = mock_ExcitationSource(model=excitation_source_model)
        nwbfile.add_device(devices=excitation_source)

        excitation_filter_model = mock_OpticalFilterModel(name="OpticalFilterModel")
        nwbfile.add_device(devices=excitation_filter_model)
        excitation_filter = mock_OpticalFilter(model=excitation_filter_model)
        nwbfile.add_device(devices=excitation_filter)

        dichroic_mirror_model = mock_DichroicMirrorModel(name="DichroicMirrorModel")
        nwbfile.add_device(devices=dichroic_mirror_model)
        dichroic_mirror = mock_DichroicMirror(model=dichroic_mirror_model)
        nwbfile.add_device(devices=dichroic_mirror)

        photodetector_model = mock_PhotodetectorModel(name="PhotodetectorModel")
        nwbfile.add_device(devices=photodetector_model)
        photodetector = mock_Photodetector(model=photodetector_model)
        nwbfile.add_device(devices=photodetector)

        emission_filter_model = mock_OpticalFilterModel(name="EmissionFilterModel")
        nwbfile.add_device(devices=emission_filter_model)
        emission_filter = mock_OpticalFilter(model=emission_filter_model)
        nwbfile.add_device(devices=emission_filter)

        microscopy_rig = mock_MicroscopyRig(
            name="MicroscopyRig",
            microscope=microscope,
            excitation_source=excitation_source,
            excitation_filter=excitation_filter,
            emission_filter=emission_filter,
            photodetector=photodetector,
            dichroic_mirror=dichroic_mirror,
        )

        planar_imaging_space = mock_PlanarImagingSpace(name="PlanarImagingSpace_1", origin_coordinates=[0.0, 0.0, 0.0])

        planar_microscopy_series_1 = mock_PlanarMicroscopySeries(
            name="PlanarMicroscopySeries_1",
            microscopy_rig=microscopy_rig,
            microscopy_channel=mock_MicroscopyChannel(name="MicroscopyChannel1"),
            planar_imaging_space=planar_imaging_space,
        )

        planar_microscopy_series_2 = mock_PlanarMicroscopySeries(
            name="PlanarMicroscopySeries_2",
            microscopy_rig=microscopy_rig,
            microscopy_channel=mock_MicroscopyChannel(name="MicroscopyChannel2"),
            planar_imaging_space=planar_imaging_space,
        )

        multi_plane_microscopy_container = mock_MultiChannelMicroscopyContainer(
            name="MultiChannelMicroscopyContainer",
            microscopy_series=[planar_microscopy_series_1, planar_microscopy_series_2],
        )

        nwbfile.add_acquisition(multi_plane_microscopy_container)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
            io.write(nwbfile)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            self.assertContainerEqual(
                multi_plane_microscopy_container, read_nwbfile.acquisition["MultiChannelMicroscopyContainer"]
            )


class TestSegmentationContainerSimpleRoundtrip(pynwb_TestCase):
    """Simple roundtrip test for SegmentationContainer."""

    def setUp(self):
        self.nwbfile_path = "test_segmentation_container_roundtrip.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        nwbfile = mock_NWBFile(session_start_time=datetime(2000, 1, 1, tzinfo=UTC))

        container = mock_SegmentationContainer(name="SegmentationContainer")
        ophys_module = nwbfile.create_processing_module(name="ophys", description="")
        ophys_module.add(container)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
            io.write(nwbfile)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            self.assertContainerEqual(container, read_nwbfile.processing["ophys"]["SegmentationContainer"])


class TestMicroscopyResponseSeriesSimpleRoundtrip(pynwb_TestCase):
    """Simple roundtrip test for MicroscopyResponseSeries."""

    def setUp(self):
        self.nwbfile_path = "test_microscopy_response_series_roundtrip.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        nwbfile = mock_NWBFile(session_start_time=datetime(2000, 1, 1, tzinfo=UTC))

        microscope_model = mock_MicroscopeModel(name="MicroscopeModel")
        nwbfile.add_device(devices=microscope_model)
        microscope = mock_Microscope(name="Microscope", model=microscope_model)
        nwbfile.add_device(devices=microscope)

        planar_imaging_space = mock_PlanarImagingSpace(name="PlanarImagingSpace")

        planar_segmentation = mock_PlanarSegmentation(
            name="PlanarSegmentation", planar_imaging_space=planar_imaging_space
        )

        segmentation_container = mock_SegmentationContainer(
            name="SegmentationContainer", segmentations=[planar_segmentation]
        )
        ophys_module = nwbfile.create_processing_module(name="ophys", description="")
        ophys_module.add(segmentation_container)

        number_of_rois = 10
        plane_segmentation_region = pynwb.ophys.DynamicTableRegion(
            name="rois",  # Name must be exactly this
            description="",
            data=[x for x in range(number_of_rois)],
            table=planar_segmentation,
        )
        microscopy_response_series = mock_MicroscopyResponseSeries(
            name="MicroscopyResponseSeries",
            rois=plane_segmentation_region,
        )

        microscopy_response_series_container = MicroscopyResponseSeriesContainer(
            name="MicroscopyResponseSeriesContainer", microscopy_response_series=[microscopy_response_series]
        )
        ophys_module.add(microscopy_response_series_container)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
            io.write(nwbfile)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            self.assertContainerEqual(microscope, read_nwbfile.devices["Microscope"])
            self.assertContainerEqual(segmentation_container, read_nwbfile.processing["ophys"]["SegmentationContainer"])

            self.assertContainerEqual(
                microscopy_response_series_container,
                read_nwbfile.processing["ophys"]["MicroscopyResponseSeriesContainer"],
            )


if __name__ == "__main__":
    pytest.main()  # Required since not a typical package structure
