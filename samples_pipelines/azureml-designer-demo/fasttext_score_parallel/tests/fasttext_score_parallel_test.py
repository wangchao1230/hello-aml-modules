import os
import sys
import unittest
from pathlib import Path

import pandas as pd
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent))
from fasttext_score_parallel import fasttext_score_parallel


class TestFasttextScoreParallel(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.base_path = Path(__file__).parent.parent / 'data'

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {'fasttext_model_dir': str(self.base_path / 'fasttext_score_parallel' / 'inputs' / 'fasttext_model_dir'),
                'char2index_dir': str(self.base_path / 'fasttext_score_parallel' / 'inputs' / 'char2index_dir'),
                'texts_to_score': str(self.base_path / 'fasttext_score_parallel' / 'inputs' / 'Texts to score')
                }

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {
            'scored_dataset_dir': str(self.base_path / 'fasttext_score_parallel' / 'outputs' / 'scored_dataset_dir')}

    def prepare_parameters(self) -> dict:
        # Change to your own parameters
        return {'param0': 'abc', 'param1': 10}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        # result.update(self.prepare_parameters())
        return result

    def prepare_argv(self):
        argv = []
        for k, v in {**self.prepare_inputs(), **self.prepare_outputs()}.items():
            argv += ['--' + k, str(v)]
        return argv

    def test_module_with_execute(self):
        # delete files created before
        result_dir = '../data/fasttext_score_parallel/outputs/scored_dataset_dir'
        if len(os.listdir(result_dir)) > 0:
            for file in os.listdir(result_dir):
                path = os.path.join(result_dir, file)
                os.remove(path)
        # This test simulates a parallel run from cmd line arguments to call fasttext_score_parallel.
        ModuleExecutor(fasttext_score_parallel).execute(self.prepare_argv())
        data_dir = '../data/fasttext_score_parallel/inputs/Texts to score'
        num_of_test_file = len(os.listdir(data_dir))
        num_of_test_result = 0
        for file in os.listdir(result_dir):
            path = os.path.join(result_dir, file)
            num = pd.read_parquet(path).shape[0]
            num_of_test_result += num
        self.assertEqual(num_of_test_file, num_of_test_result)
