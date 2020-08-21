import os
import sys
import unittest
from pathlib import Path

import pandas as pd
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fasttext_score import fasttext_score


class TestFasttextScore(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.base_path = Path(__file__).parent.parent.parent

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {'fasttext_model_dir': str(self.base_path / 'fasttext_train' / 'data' / 'fasttext_train'
                                          / 'outputs' / 'trained_model_dir'),
                'texts_to_score': str(self.base_path / 'fasttext_score' / 'data' / 'fasttext_score'
                                      / 'inputs' / 'input_files')
                }

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {
            'scored_data_output_dir': str(self.base_path / 'fasttext_score' / 'data'
                                          / 'fasttext_score' / 'outputs' / 'scored_data_output_dir')}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        return result

    def prepare_argv(self):
        argv = []
        for k, v in {**self.prepare_inputs(), **self.prepare_outputs()}.items():
            argv += ['--' + k, str(v)]
        return argv

    def test_module_with_execute(self):
        # delete files created before
        result_dir = self.prepare_outputs()['scored_data_output_dir']
        os.makedirs(result_dir, exist_ok=True)
        if len(os.listdir(result_dir)) > 0:
            for file in os.listdir(result_dir):
                path = os.path.join(result_dir, file)
                os.remove(path)
        # This test simulates a parallel run from cmd line arguments to call fasttext_score_parallel.
        ModuleExecutor(fasttext_score).execute(self.prepare_argv())
        data_dir = self.prepare_inputs()['texts_to_score']
        os.makedirs(data_dir, exist_ok=True)
        num_of_test_file = len(os.listdir(data_dir))
        num_of_test_result = 0
        for file in os.listdir(result_dir):
            path = os.path.join(result_dir, file)
            num = pd.read_parquet(path).shape[0]
            num_of_test_result += num
        self.assertEqual(num_of_test_file, num_of_test_result)
