import os
import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent))
from compare_two_models import compare_two_models


class TestCompareTwoModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent.parent.parent

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {
            'first_trained_model': str(self.base_path / 'fasttext_train' / 'data' / 'fasttext_train'
                                       / 'outputs' / 'trained_model_dir'),
            'first_trained_result': str(self.base_path / 'fasttext_evaluation' / 'data'
                                        / 'fasttext_evaluation' / 'outputs' / 'model_testing_result'),
            'second_trained_model': str(self.base_path / 'fasttext_train' / 'data' / 'fasttext_train'
                                        / 'outputs' / 'trained_model_dir'),
            'second_trained_result': str(self.base_path / 'fasttext_evaluation' / 'data'
                                         / 'fasttext_evaluation' / 'outputs' / 'model_testing_result')
        }

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {'the_better_model': str(self.base_path / 'compare_two_models' / 'data'
                                        / 'compare_two_models'/'outputs' / 'the_better_model')}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        return result

    def test_module_from_func(self):
        paths = self.prepare_outputs()
        for path in paths.values():
            os.makedirs(path, exist_ok=True)
        # This test calls compare_two_models from cmd line arguments.
        local_module = Module.from_func(self.workspace, compare_two_models)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        status = module.run(use_docker=True)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        dir_ = self.prepare_outputs()['the_better_model']
        os.makedirs(dir_, exist_ok=True)
        # This test calls compare_two_models from parameters directly.
        compare_two_models(**self.prepare_arguments())
        # check the existence of BestModel
        path = os.path.join(dir_, 'BestModel')
        self.assertTrue(os.path.exists(path))
