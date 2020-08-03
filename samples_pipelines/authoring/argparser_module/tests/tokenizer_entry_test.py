import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent))
from tokenizer_entry import tokenizer


class TestTokenizerEntry(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent.parent / 'data'

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {'input_file_path': str(self.base_path / 'tokenizer_entry' / 'inputs' / 'input_file_path')}

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {}

    def prepare_parameters(self) -> dict:
        # Change to your own parameters
        return {'output_dir_path': '', 'output_to_file': 0, 'input_is_tsv': 0, 'delimiter': '', 'ignore_cols': 0, 'mode': 'train', 'type': 'word'}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        result.update(self.prepare_parameters())
        return result

    def test_module_from_func(self):
        # This test calls tokenizer from cmd line arguments.
        local_module = Module.from_func(self.workspace, tokenizer)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        module.set_parameters(**self.prepare_parameters())
        status = module.run(use_docker=True)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        # This test calls tokenizer from parameters directly.
        tokenizer(**self.prepare_arguments())
