import os
import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent))
from fasttext_evaluation import fasttext_evaluation


class TestFasttextEvaluation(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent.parent.parent

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {
            'trained_model_dir': str(self.base_path / 'fasttext_train' / 'data' / 'fasttext_train'
                                     / 'outputs' / 'trained_model_dir'),
            'test_data_dir': str(self.base_path / 'split_data_txt' / 'data' / 'split_data_txt'
                                       / 'outputs' / 'test_data_output')
        }

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {'model_testing_result': str(self.base_path / 'fasttext_evaluation' / 'data'
                                            / 'fasttext_evaluation' / 'outputs' / 'model_testing_result')}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        return result

    def test_module_from_func(self):
        # This test calls fasttext_evaluation from cmd line arguments.
        local_module = Module.from_func(self.workspace, fasttext_evaluation)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        status = module.run(use_docker=True)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        paths = self.prepare_outputs()
        for path in paths.values():
            os.makedirs(path, exist_ok=True)
        # This test calls fasttext_evaluation from parameters directly.
        fasttext_evaluation(**self.prepare_arguments())
        # check the existence of result.json
        path_result = os.path.join(self.prepare_outputs()['model_testing_result'], 'result.json')
        self.assertTrue(os.path.exists(path_result))
