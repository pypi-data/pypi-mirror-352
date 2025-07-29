from ewokscore import Task
import subprocess
from pathlib import Path


class H5ToNx(
    Task, input_names=["bliss_hdf5_path", "output_dir"], output_names=["nx_path"]
):

    def run(self):
        """
        Executes a subprocess that runs nxtomomill to convert the input_scan to nx format
        :return: The path to the created nx file
        """

        command = [
            "nxtomomill",
            "h52nx",
            self.inputs.bliss_hdf5_path,
            self.inputs.output_dir,
        ]
        subprocess.run(command, capture_output=True, text=True, check=True)
        input_path = Path(self.inputs.bliss_hdf5_path)
        output_dir = Path(self.inputs.output_dir)
        new_filename = input_path.stem + ".nx"
        self.outputs.nx_path = str(output_dir / new_filename)
