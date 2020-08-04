import sys
import unittest
from pathlib import Path
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor

sys.path.append(str(Path(__file__).parent.parent))
from parallel_score import parallel_score_images


def get_files(paths):
    results = []
    for path in paths:
        if path is not None:
            results += [str(f) for f in Path(path).iterdir()]
    return results


class TestParallelScore(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.base_path = Path(__file__).parent / 'parallel_score_images'

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {
            'trained_model': str(self.base_path / 'inputs' / 'trained_model'),
            'images_to_score': str(self.base_path / 'inputs' / 'images_to_score'),
            'optional_images_to_score': str(self.base_path / 'inputs' / 'optional_images_to_score'),
        }

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {'scored_dataset': str(self.base_path / 'outputs' / 'scored_dataset')}

    def prepare_parameters(self) -> dict:
        # Change to your own parameters
        return {}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        result.update(self.prepare_parameters())
        return result

    def prepare_argv(self):
        argv = []
        for k, v in {**self.prepare_inputs(), **self.prepare_outputs(), **self.prepare_parameters(), }.items():
            argv += ['--' + k, str(v)]
        return argv

    def test_module_with_execute(self):
        # This test simulates a parallel run from cmd line arguments to call parallel_sample.
        ModuleExecutor(parallel_score_images).execute(self.prepare_argv())
