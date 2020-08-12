import os
import sys
import json
from pathlib import Path

import torch
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl

from common.utils import load_dataset, DataIter, test, get_vocab, get_id_label


@dsl.module(
    name="FastText Evaluation",
    version='0.0.7',
    description='Evaluate the trained FastText model'
)
def fasttext_evaluation(
        model_testing_result: OutputDirectory(),
        trained_model_dir: InputDirectory() = None,
        test_data_dir: InputDirectory() = None
):
    # hardcode: word_to_index.json, data.txt, BestModel, and result.json
    print('=====================================================')
    print(f'trained_model_dir: {Path(trained_model_dir).resolve()}')
    print(f'test_data_dir: {Path(test_data_dir).resolve()}')
    path_word_to_index = os.path.join(test_data_dir, 'word_to_index.json')
    word_to_index = get_vocab(path_word_to_index)
    path_label = os.path.join(test_data_dir, 'label.txt')
    map_id_label, map_label_id = get_id_label(path_label)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    max_len_ = 38
    path = os.path.join(test_data_dir, 'data.txt')
    test_samples = load_dataset(file_path=path, max_len=max_len_, word_to_index=word_to_index,
                                map_label_id=map_label_id)
    test_iter = DataIter(test_samples)
    path = os.path.join(trained_model_dir, 'BestModel')
    model = torch.load(f=path)
    os.makedirs(model_testing_result, exist_ok=True)
    path = os.path.join(model_testing_result, 'result.json')
    acc_ = test(model, test_iter, device)
    json.dump({"acc": acc_}, open(path, 'w'))
    print('\n============================================')


if __name__ == '__main__':
    ModuleExecutor(fasttext_evaluation).execute(sys.argv)
