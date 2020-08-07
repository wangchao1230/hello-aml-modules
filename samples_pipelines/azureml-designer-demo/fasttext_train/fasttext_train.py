import os
import sys
import time
import torch

from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from common.FastText import FastText

from common.utils import get_vocab, get_classs, load_dataset, DataIter, train


@dsl.module(
    name="FastText Train",
    version='0.0.40',
    description='Train the FastText model. You could adjust the hyperparameters conveniently'
)
def fasttext_train(
        trained_model_dir: OutputDirectory(type='ModelDirectory'),
        training_data_dir: InputDirectory() = None,
        validation_data_dir: InputDirectory() = None,
        char2index_dir: InputDirectory() = None,
        epochs=1,
        batch_size=64,
        learning_rate=0.0005,
        embedding_dim=128
):
    # hardcode: character2index.json and data.txt
    print('============================================')
    print('training_data_dir:', training_data_dir)
    print('validation_data_dir:', validation_data_dir)
    char2index_dir = os.path.join(char2index_dir, 'character2index.json')
    c2i = get_vocab(char2index_dir)
    class_ = get_classs()
    max_len_ = 38
    n_class_ = len(class_)
    vocab_size_ = len(c2i)
    stop_patience = 5
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    path = os.path.join(training_data_dir, 'data.txt')
    train_samples = load_dataset(file_path=path, max_len=max_len_, char2index_dir=char2index_dir)
    path = os.path.join(validation_data_dir, 'data.txt')
    dev_samples = load_dataset(file_path=path, max_len=max_len_, char2index_dir=char2index_dir)
    print('train_samples.shape:{}'.format(train_samples.shape))
    print('dev_samples.shape:{}'.format(dev_samples.shape))
    train_iter = DataIter(train_samples, batch_size)
    dev_iter = DataIter(dev_samples, batch_size)

    model = FastText(vocab_size=vocab_size_, n_class=n_class_, embed_dim=embedding_dim)
    start = time.time()
    train(model, trained_model_dir, train_iter, dev_iter=dev_iter, epochs=epochs, learning_rate=learning_rate,
          stop_patience=stop_patience, device=device)
    end = time.time()
    print('\nspent time: %.2f sec' % (end - start))
    print('============================================')


if __name__ == '__main__':
    ModuleExecutor(fasttext_train).execute(sys.argv)
