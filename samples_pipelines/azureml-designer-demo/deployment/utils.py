import os
import json

import torch
import numpy as np
from tqdm import tqdm
from azureml.core import Run

torch.manual_seed(1)
torch.cuda.manual_seed_all(1)
np.random.seed(1)


def predict(model, data_iter, device):
    model.eval()
    # for metrics
    run = Run.get_context()
    p_ = 0
    for x, y in data_iter:
        dev_x_ = torch.LongTensor(x).to(device)
        outputs = model(dev_x_)
        p_ = torch.max(outputs.data, 0)[1].cpu()
        run.log(name='Prediction Result', value=get_classs_reverse()[int(p_)])
    return get_classs_reverse()[int(p_)]


def get_vocab(char2index_dir):
    c2i = json.load(open(char2index_dir, 'r', encoding='utf-8'))
    return c2i


def get_classs():
    res = {'finance': 0,
           'realty': 1,
           'stocks': 2,
           'education': 3,
           'science': 4,
           'society': 5,
           'politics': 6,
           'sports': 7,
           'game': 8,
           'entertainment': 9}
    return res


def get_classs_reverse():
    res = {0: 'finance',
           1: 'realty',
           2: 'stocks',
           3: 'education',
           4: 'science',
           5: 'society',
           6: 'politics',
           7: 'sports',
           8: 'game',
           9: 'entertainment'}
    return res


def shuffle_samples(samples):
    samples = np.array(samples)
    shffle_index = np.arange(len(samples))
    np.random.shuffle(shffle_index)
    samples = samples[shffle_index]
    return samples


def load_dataset(file_path='', max_len=38, char2index_dir=''):
    c2i = get_vocab(char2index_dir)
    pad_id = c2i.get('[PAD]', 0)
    samples = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            texts = f.read().split("\n")
            texts = [item.strip() for item in texts if len(item) > 0]
        for line in tqdm(texts, desc="character to index"):
            line_s = line.split('\t')
            if len(line_s) < 2:
                continue
            context, label = line_s[0], line_s[1]
            line_data = ([c2i.get(c, 1) for c in context]) + [pad_id] * (max_len - len(context))
            line_data = line_data[:max_len]
            samples.append((line_data, int(label)))
    # for prediction
    else:
        context = file_path
        line_data = ([c2i.get(c, 1) for c in context]) + [pad_id] * (max_len - len(context))
        line_data = line_data[:max_len]
        samples.append((line_data, 0))  # fake label

    samples = np.array(samples)

    return samples


class DataIter(object):
    def __init__(self, samples, batch_size=32, shuffle=True):
        if shuffle:
            samples = shuffle_samples(samples)
        self.samples = samples
        self.batch_size = batch_size
        self.n_batches = len(samples) // self.batch_size
        self.residue = (len(samples) % self.n_batches != 0)
        self.index = 0

    def split_samples(self, sub_samples):
        b_x = [item[0] for item in sub_samples]
        b_y = [item[1] for item in sub_samples]
        return np.array(b_x), np.array(b_y)

    def __next__(self):
        if (self.index == self.n_batches) and (self.residue is True):
            sub_samples = self.samples[self.index * self.batch_size: len(self.samples)]
            self.index += 1
            return self.split_samples(sub_samples)
        elif self.index >= self.n_batches:
            self.index = 0
            raise StopIteration
        else:
            sub_samples = self.samples[self.index * self.batch_size: (self.index + 1) * self.batch_size]
            self.index += 1
            return self.split_samples(sub_samples)

    def __iter__(self):
        return self

    def __len__(self):
        if self.residue:
            return self.n_batches + 1
        else:
            return self.n_batches
