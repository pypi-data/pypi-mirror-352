import pytest
import sys
import os
from ewokstomo.tasks.buildgallery import BuildGallery
from pathlib import Path
import importlib.resources as pkg_resources
import numpy as np
from PIL import Image


def get_data_file(file_name, extension="h5", flats=False, darks=False):
    if sys.version_info >= (3, 10):
        if darks:
            suffix = "_darks"
        elif flats:
            suffix = "_flats"
        else:
            suffix = ""
        file_path = pkg_resources.files(f"ewokstomo.tests.data.{file_name}").joinpath(
            f"{file_name}{suffix}.{extension}"
        )
    else:
        file_path = Path(__file__).parent / "data" / file_name / f"{file_name}.nx"
    return file_path


def create_dummy_image(shape=(10, 10)) -> np.ndarray:
    """Helper: create a gradient float image array."""
    return np.linspace(0, 255, num=shape[0] * shape[1], dtype=float).reshape(shape)


@pytest.fixture
def simple_image() -> np.ndarray:
    """Fixture providing a basic gradient image."""
    return create_dummy_image((10, 10))


@pytest.mark.order(5)
@pytest.mark.parametrize("Task", [BuildGallery])
def test_buildgallery_task(Task, tmpdir):
    nx_file_path = get_data_file("TestEwoksTomo_0010", "nx")
    reduced_darks_path = get_data_file("TestEwoksTomo_0010", "hdf5", darks=True)
    reduced_flats_path = get_data_file("TestEwoksTomo_0010", "hdf5", flats=True)
    task = Task(
        inputs={
            "nx_path": str(nx_file_path),
            "reduced_darks_path": str(reduced_darks_path),
            "reduced_flats_path": str(reduced_flats_path),
        },
    )
    task.run()

    # Check gallery directory
    gallery_path = Path(task.outputs.processed_data_dir) / "gallery"
    assert gallery_path.exists(), "Gallery directory does not exist"
    assert gallery_path.is_dir(), "Gallery path is not a directory"

    # Collect generated images
    images = sorted(gallery_path.glob("*.png"))
    assert len(images) == 5, f"Expected 5 images, found {len(images)}"

    for img_path in images:
        # Check basic file format
        img = Image.open(img_path)
        assert img.format == "PNG", f"{img_path.name} is not a valid PNG image"
        assert img.mode == "L", f"{img_path.name} is not grayscale"
        assert (
            img.size[0] > 0 and img.size[1] > 0
        ), f"{img_path.name} has invalid dimensions"

        # Check pixel values range
        arr = np.array(img)
        assert arr.dtype == np.uint8, f"{img_path.name} not saved as 8-bit"
        assert (
            arr.max() <= 255 and arr.min() >= 0
        ), f"{img_path.name} has out-of-bound pixel values"

        # Optional: check that inversion occurred (at least some black and white variation)
        unique_vals = np.unique(arr)
        assert (
            len(unique_vals) > 1
        ), f"{img_path.name} appears to be flat (no intensity variation)"

        # Optional: filename pattern
        assert img_path.name.startswith(
            "image_"
        ), f"{img_path.name} does not follow naming convention"

    @pytest.mark.order(6)
    def test_save_to_gallery_bounds(simple_image):
        bounds = (50.0, 200.0)
        nx_file_path = get_data_file("TestEwoksTomo_0010", "nx")
        reduced_darks_path = get_data_file("TestEwoksTomo_0010", "hdf5", darks=True)
        reduced_flats_path = get_data_file("TestEwoksTomo_0010", "hdf5", flats=True)
        task = BuildGallery(
            inputs={
                "nx_path": str(nx_file_path),
                "reduced_darks_path": str(reduced_darks_path),
                "reduced_flats_path": str(reduced_flats_path),
                "bounds": bounds,
            },
        )
        task.gallery_overwrite = True
        task.gallery_output_binning = 1
        gallery_file = nx_file_path.parent / "gallery" / "image_bounds_0.png"
        task.save_to_gallery(gallery_file, simple_image)
        assert gallery_file.exists(), "Gallery file was not created"

    @pytest.mark.order(7)
    @pytest.mark.parametrize("anglestep_and_nbimages", [(45, 9), (90, 5), (180, 3)])
    def test_buildgallery_angles(anglestep_and_nbimages):
        nx_file_path = get_data_file("TestEwoksTomo_0010", "nx")
        gallery_dir = nx_file_path.parent / "gallery"
        if os.path.exists(gallery_dir):
            os.remove(gallery_dir)
        reduced_darks_path = get_data_file("TestEwoksTomo_0010", "hdf5", darks=True)
        reduced_flats_path = get_data_file("TestEwoksTomo_0010", "hdf5", flats=True)
        angle_step, nb_images = anglestep_and_nbimages
        task = BuildGallery(
            inputs={
                "nx_path": str(nx_file_path),
                "reduced_darks_path": str(reduced_darks_path),
                "reduced_flats_path": str(reduced_flats_path),
                "angle_step": angle_step,
            },
        )

        task.run()
        assert (
            len(images) == nb_images
        ), f"Expected {nb_images} images, found {len(images)}"
