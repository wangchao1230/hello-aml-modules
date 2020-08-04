import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

from azureml.pipeline.wrapper.dsl._utils import _change_working_dir
from xmlrunner import xmlrunner

sys.path.insert(0, str(Path(__file__).parent.parent))
from basic_module import basic_module


class TestModuleRunRelativePath(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent / 'config.json'))

    def test_relative(self):
        local_module = Module.from_func(self.workspace, basic_module)
        module = local_module()
        with _change_working_dir(Path(__file__).parent.parent):
            module.set_inputs(
                input_dir='data/basic_module/inputs/input_dir'
            )
            module.set_parameters(
                str_param='local_test'
            )
            status = module.run(use_docker=False)
            self.assertEqual(status, 'Completed', 'Module run failed.')


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner())
