import os
import sys
import json
import time
import torch
import shutil

from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory

from common.FastText import FastText
from common.utils import get_vocab, get_id_label, load_dataset, DataIter, train


@dsl.module(
    name="FastText Train",
    version='0.0.41',
    description='Train the fastText model.',
    base_image='mcr.microsoft.com/azureml/intelmpi2018.3-cuda10.0-cudnn7-ubuntu16.04'
)
def fasttext_train(
        trained_model_dir: OutputDirectory(type='ModelDirectory'),
        training_data_dir: InputDirectory() = None,
        validation_data_dir: InputDirectory() = None,
        epochs=1,
        batch_size=64,
        max_len=32,
        embed_dim=300,
        hidden_size=256,
        ngram_size=200000,
        dropout=0.5,
        learning_rate=0.001

):
    print('============================================')
    print('training_data_dir:', training_data_dir)
    print('validation_data_dir:', validation_data_dir)
    path_word_to_index = os.path.join(training_data_dir, 'word_to_index.json')
    word_to_index = get_vocab(path_word_to_index)
    path_label = os.path.join(training_data_dir, 'label.txt')
    map_id_label, map_label_id = get_id_label(path_label)
    class_num = len(map_id_label)
    vocab_size = len(word_to_index)
    stop_patience = 5
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('device:', device)
    # load training dataset
    path = os.path.join(training_data_dir, 'data.txt')
    train_samples = load_dataset(file_path=path, word_to_index=word_to_index, map_label_id=map_label_id,
                                 max_len=max_len, ngram_size=ngram_size)
    train_iter = DataIter(samples=train_samples, batch_size=batch_size, shuffle=True, device=device)
    # load validation dataset
    path = os.path.join(validation_data_dir, 'data.txt')
    dev_samples = load_dataset(file_path=path, word_to_index=word_to_index, map_label_id=map_label_id,
                               max_len=max_len, ngram_size=ngram_size)
    dev_iter = DataIter(samples=dev_samples, batch_size=batch_size, shuffle=True, device=device)

    model = FastText(vocab_size=vocab_size, class_num=class_num, dropout=dropout, embed_dim=embed_dim,
                     hidden_size=hidden_size, ngram_size=ngram_size)
    # watch parameters
    print(model.parameters)
    # copy word_to_index.json and label.txt for later scoring.
    shutil.copy(src=path_word_to_index, dst=trained_model_dir)
    shutil.copy(src=path_label, dst=trained_model_dir)
    # shared parameters for loading dataset
    shared_params = {'max_len': max_len, 'ngram_size': ngram_size}
    path = os.path.join(trained_model_dir, 'shared_params.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(shared_params, f)
    start = time.time()
    train(model, trained_model_dir, train_iter=train_iter, dev_iter=dev_iter, epochs=epochs,
          learning_rate=learning_rate, stop_patience=stop_patience, device=device)
    end = time.time()
    print('\nduration of training process: %.2f sec' % (end - start))
    print('============================================')


if __name__ == '__main__':
    ModuleExecutor(fasttext_train).execute(sys.argv)
