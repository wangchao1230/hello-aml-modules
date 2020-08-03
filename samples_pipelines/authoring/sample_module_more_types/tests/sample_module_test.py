import sys
import unittest
from pathlib import Path
import xmlrunner

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

sys.path.append(str(Path(__file__).parent.parent))
from sample_module import sample_module
from my_data_type import MyEnum


class TestSampleModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent
        cls.outputs = cls.base_path / 'outputs'

    def prepare_parameters(self) -> dict:
        return {
            'str_param': 'str_param',
            'int_param': '0',
            'float_param': '0.2',
            'bool_param': True,
            'enum_param': MyEnum.Enum1.name
        }

    def prepare_inputs(self) -> dict:
        return {'input_data0': str(self.base_path / 'inputs' / 'input_data0')}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        inputs = self.prepare_inputs()
        for input in inputs:
            inputs[input] = Path(inputs[input])
        result.update(inputs)
        result.update(self.prepare_parameters())
        return result

    def test_module_from_func(self):
        # This test calls basic_module from cmd line arguments.
        local_module = Module.from_func(self.workspace, sample_module)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        module.set_parameters(**self.prepare_parameters())
        status = module.run(working_dir=str(self.outputs), use_docker=False)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        # This test calls basic_module from parameters directly.
        result = sample_module(**self.prepare_arguments())
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner())
