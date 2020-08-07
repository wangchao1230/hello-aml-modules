import os
import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent))
from split_data_txt import split_data_txt


class TestSplitDataTxt(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent.parent / 'data'

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {'input_dir': str(self.base_path / 'split_data_txt' / 'inputs' / 'input_dir')}

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {
            'training_data_output': str(self.base_path / 'split_data_txt' / 'outputs' / 'training_data_output'),
            'validation_data_output': str(self.base_path / 'split_data_txt' / 'outputs' / 'validation_data_output'),
            'test_data_output': str(self.base_path / 'split_data_txt' / 'outputs' / 'test_data_output')
        }

    def prepare_parameters(self) -> dict:
        # Change to your own parameters
        return {
            'training_data_ratio': 0.65,
            'validation_data_ratio': 0.15,
            'random_split': False,
            'seed': 123
        }

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        result.update(self.prepare_parameters())
        return result

    def test_module_from_func(self):
        # This test calls split_data_txt from cmd line arguments.
        local_module = Module.from_func(self.workspace, split_data_txt)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        module.set_parameters(**self.prepare_parameters())
        status = module.run(use_docker=True)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        # This test calls split_data_txt from parameters directly.
        split_data_txt(**self.prepare_arguments())
        # check ratio
        params = self.prepare_arguments()
        training_data_ratio = params['training_data_ratio']
        validation_data_ratio = params['validation_data_ratio']
        path_input = os.path.join(self.prepare_inputs()['input_dir'], 'data.txt')
        num_total = len(open(path_input, 'r', encoding='utf-8').readlines())

        paths = self.prepare_outputs()
        path_training_data_output = os.path.join(paths['training_data_output'], 'data.txt')
        path_validation_data_output = os.path.join(paths['validation_data_output'], 'data.txt')
        path_test_data_output = os.path.join(paths['test_data_output'], 'data.txt')

        num_train = len(open(path_training_data_output, 'r', encoding='utf-8').readlines())
        num_validation = len(open(path_validation_data_output, 'r', encoding='utf-8').readlines())
        num_test = len(open(path_test_data_output, 'r', encoding='utf-8').readlines())

        expected_num_train = int(num_total * training_data_ratio)
        expected_num_validation = int(num_total * validation_data_ratio)
        expected_num_test = num_total - expected_num_train - expected_num_validation
        # check ratio
        self.assertEqual(num_train, expected_num_train)
        self.assertEqual(num_validation, expected_num_validation)
        self.assertEqual(num_test, expected_num_test)
