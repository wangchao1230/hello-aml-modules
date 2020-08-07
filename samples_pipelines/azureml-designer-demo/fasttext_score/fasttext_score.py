import os
import sys
from pathlib import Path

import torch
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory
from azureml.pipeline.wrapper import dsl

from common.utils import load_dataset, DataIter, predict


@dsl.module(
    name="FastText Score",
    version='0.0.21',
    description='Predict the category of the input sentence'
)
def fasttext_score(
        input_sentence='I like playing football very much',
        fasttext_model_dir: InputDirectory() = '.',
        char2index_dir: InputDirectory() = None
):
    # hardcode: character2index.json and BestModel
    print('=====================================================')
    print(f'fasttext_model_dir: {Path(fasttext_model_dir).resolve()}')
    print(f'char2index_dir: {Path(char2index_dir).resolve()}')
    print(f'input_sentence: {input_sentence}')
    char2index_dir = os.path.join(char2index_dir, 'character2index.json')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    max_len_ = 38
    path = input_sentence
    test_samples = load_dataset(file_path=path, max_len=max_len_, char2index_dir=char2index_dir)
    test_iter = DataIter(test_samples, batch_size=1)
    path = os.path.join(fasttext_model_dir, 'BestModel')
    model = torch.load(f=path)
    res = predict(model, test_iter, device)
    print('the category of "%s" is %s' % (input_sentence, res))
    print('=====================================================')


if __name__ == '__main__':
    ModuleExecutor(fasttext_score).execute(sys.argv)
