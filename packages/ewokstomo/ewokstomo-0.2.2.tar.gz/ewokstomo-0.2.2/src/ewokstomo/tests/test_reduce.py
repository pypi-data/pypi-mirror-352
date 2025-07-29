import pytest
import os
import sys
from ewokstomo.tasks.reducedarkflat import ReduceDarkFlat
from ewoks import execute_graph
from pathlib import Path
import importlib.resources as pkg_resources


def get_json_file(file_name):
    if sys.version_info >= (3, 10):
        file_path = pkg_resources.files("ewokstomo.workflows").joinpath(file_name)
    else:
        file_path = Path(__file__).resolve().parents[1] / "workflows" / file_name
    return file_path


def get_data_file(file_name):
    if sys.version_info >= (3, 10):
        file_path = pkg_resources.files(f"ewokstomo.tests.data.{file_name}").joinpath(
            f"{file_name}.nx"
        )
    else:
        file_path = Path(__file__).parent / "data" / file_name / f"{file_name}.nx"
    return file_path


@pytest.mark.order(1)
@pytest.mark.parametrize("Task", [ReduceDarkFlat])
def test_reducedarkflat_task(Task, tmpdir):
    nx_file_path = get_data_file("TestEwoksTomo_0010")

    task = Task(
        inputs={
            "nx_path": str(nx_file_path),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    task.run()

    expected_darks_path = str(nx_file_path).replace(".nx", "_darks.hdf5")
    expected_flats_path = str(nx_file_path).replace(".nx", "_flats.hdf5")
    assert str(task.outputs.reduced_darks_path) == expected_darks_path
    assert str(task.outputs.reduced_flats_path) == expected_flats_path
    # assert Path(expected_darks_path).is_file()
    # assert Path(expected_flats_path).is_file()
    # Clean up the generated files
    if os.path.exists(expected_darks_path):
        os.remove(expected_darks_path)
    if os.path.exists(expected_flats_path):
        os.remove(expected_flats_path)


@pytest.mark.order(2)
@pytest.mark.parametrize("workflow", ["reducedarkflat.json"])
def test_reducedarkflat_workflow(workflow, tmpdir):
    nx_file_path = get_data_file("TestEwoksTomo_0010")
    workflow_file_path = get_json_file(workflow)

    output = execute_graph(
        workflow_file_path,
        inputs=[
            {
                "name": "nx_path",
                "value": str(nx_file_path),
            }
        ],
    )

    expected_darks_path = str(nx_file_path).replace(".nx", "_darks.hdf5")
    expected_flats_path = str(nx_file_path).replace(".nx", "_flats.hdf5")

    assert str(output["reduced_darks_path"]) == expected_darks_path
    assert str(output["reduced_flats_path"]) == expected_flats_path
