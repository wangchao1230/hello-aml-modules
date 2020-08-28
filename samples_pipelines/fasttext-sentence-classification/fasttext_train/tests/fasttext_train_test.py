import os
import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent))
from fasttext_train import fasttext_train


class TestFasttextTrain(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent.parent.parent

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {
            'training_data_dir': str(self.base_path / 'split_data_txt' / 'data' / 'split_data_txt'
                                     / 'outputs' / 'training_data_output'),
            'validation_data_dir': str(self.base_path / 'split_data_txt' / 'data' / 'split_data_txt'
                                       / 'outputs' / 'validation_data_output')
        }

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {'trained_model_dir': str(
            self.base_path / 'fasttext_train' / 'data' / 'fasttext_train' / 'outputs' / 'trained_model_dir')}

    def prepare_parameters(self) -> dict:
        # Change to your own parameters
        return {'epochs': 3,
                'batch_size': 128,
                'max_len': 233,
                'embed_dim': 300,
                'hidden_size': 256,
                'ngram_size': 300000,
                'learning_rate': 0.001
                }

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        result.update(self.prepare_parameters())
        return result

    def test_module_from_func(self):
        # This test calls fasttext_train from cmd line arguments.
        local_module = Module.from_func(self.workspace, fasttext_train)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        module.set_parameters(**self.prepare_parameters())
        status = module.run(use_docker=True)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        paths = self.prepare_outputs()
        for path in paths.values():
            os.makedirs(path, exist_ok=True)
        # This test calls fasttext_train from parameters directly.
        fasttext_train(**self.prepare_arguments())
        # Check the existence of BestModel
        path_model = os.path.join(self.prepare_outputs()['trained_model_dir'], 'BestModel')
        self.assertTrue(os.path.exists(path_model))
