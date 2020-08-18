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
    version='0.0.8',
    description='Evaluate the trained fastText model',
    base_image='mcr.microsoft.com/azureml/intelmpi2018.3-cuda10.0-cudnn7-ubuntu16.04'
)
def fasttext_evaluation(
        model_testing_result: OutputDirectory(),
        trained_model_dir: InputDirectory() = None,
        test_data_dir: InputDirectory() = None
):
    print('=====================================================')
    print(f'trained_model_dir: {Path(trained_model_dir).resolve()}')
    print(f'test_data_dir: {Path(test_data_dir).resolve()}')
    path_word_to_index = os.path.join(test_data_dir, 'word_to_index.json')
    word_to_index = get_vocab(path_word_to_index)
    path_label = os.path.join(test_data_dir, 'label.txt')
    map_id_label, map_label_id = get_id_label(path_label)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('device:', device)
    path = os.path.join(trained_model_dir, 'shared_params.json')
    with open(path, 'r', encoding='utf-8') as f:
        shared_params = json.load(f)
    path = os.path.join(test_data_dir, 'data.txt')
    test_samples = load_dataset(file_path=path, max_len=shared_params['max_len'],
                                ngram_size=shared_params['ngram_size'], word_to_index=word_to_index,
                                map_label_id=map_label_id)
    test_iter = DataIter(samples=test_samples, shuffle=False, device=device)
    path = os.path.join(trained_model_dir, 'BestModel')
    model = torch.load(f=path, map_location=device)
    path = os.path.join(model_testing_result, 'result.json')
    acc_ = test(model, test_iter)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"acc": acc_}, f)
    print('\n============================================')


if __name__ == '__main__':
    ModuleExecutor(fasttext_evaluation).execute(sys.argv)
