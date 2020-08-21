# -*- coding: utf-8 -*-
import os
import json
import torch
import random
import numpy as np
from tqdm import tqdm
from sklearn import metrics
from azureml.pipeline.wrapper.dsl.module import OutputDirectory
from azureml.core import Run

torch.manual_seed(1)
np.random.seed(1)


def train(model, trained_model_dir: OutputDirectory(type='AnyDirectory'), train_iter, dev_iter=None,
          epochs=20, learning_rate=0.0001, stop_patience=3, device=None):
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print('device:', device)

    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    model.to(device)
    loss = torch.nn.CrossEntropyLoss()

    min_loss_epoch = (None, None)
    stop_flag = False

    model_name = model._get_name()
    # for metrics
    run = Run.get_context()
    for epoch in range(epochs):
        loss_value_list = []
        total_iter = len(train_iter)
        for i, (btach_x, btach_y) in enumerate(train_iter):
            outputs = model(btach_x)
            optimizer.zero_grad()
            loss_value = loss(outputs, btach_y)
            loss_value.backward()
            optimizer.step()
            loss_value_list.append(loss_value.cpu().data.numpy())
            # for metrics
            run.log(name='CrossEntropyLoss', value=np.mean(loss_value_list))
            if i % 50 == 0:
                str_ = f"{model_name} epoch:{epoch + 1}/{epochs} step:{i + 1}/{total_iter} mean_loss:{np.mean(loss_value_list): .4f}"
                print(str_)

            if (i + 1) == total_iter and dev_iter is not None:
                loss_, acc_, prec_, recall_, f1_ = evaluation(model, dev_iter)
                str_ = f" validation loss:{loss_:.4f}  acc:{acc_:.4f}"
                print(str_)
                model.train()

                if (min_loss_epoch[0] is None) or (min_loss_epoch[0] > loss_):
                    min_loss_epoch = (loss_, epoch)
                    os.makedirs(trained_model_dir, exist_ok=True)
                    path = os.path.join(trained_model_dir, "BestModel")
                    torch.save(obj=model, f=path)
                else:
                    if (epoch - min_loss_epoch[1]) >= stop_patience:
                        stop_flag = True
                        break

        if stop_flag is True:
            break


def test(model, test_iter=None):
    run = Run.get_context()
    loss_, acc_, prec_, recall_, f1_ = evaluation(model, test_iter)
    # for metrics
    run.log(name='CrossEntropyLoss', value=loss_)
    run.log(name='Accuracy', value=acc_)
    run.log(name='Precision', value=prec_)
    run.log(name='Recall', value=recall_)
    run.log(name='F1', value=f1_)
    str_ = f"test acc:{acc_:.4f}"
    print(str_)
    return acc_


def evaluation(model, data_iter):
    model.eval()
    with torch.no_grad():
        acc_list = []
        precision_list = []
        recall_list = []
        f1_list = []
        loss_list = []
        loss = torch.nn.CrossEntropyLoss()
        for btach_x, btach_y in data_iter:
            outputs = model(btach_x)
            p_ = torch.max(outputs.data, 1)[1].cpu().numpy()
            y = btach_y.cpu()
            acc_ = metrics.accuracy_score(y, p_)
            precision_ = metrics.precision_score(y, p_, average='macro')
            recall_ = metrics.recall_score(y, p_, average='macro')
            f1_ = metrics.f1_score(y, p_, average='macro')
            loss_ = loss(outputs, btach_y)
            acc_list.append(acc_)
            precision_list.append(precision_)
            recall_list.append(recall_)
            f1_list.append(f1_)
            loss_list.append(loss_.cpu().data.numpy())

        return np.mean(loss_list), np.mean(acc_list), np.mean(precision_list), np.mean(recall_list), np.mean(f1_list)


def predict(model, data_iter, map_id_label):
    model.eval()
    # for metrics
    run = Run.get_context()
    p_ = 0
    for batch_x, batch_y in data_iter:
        outputs = model(batch_x)
        p_ = torch.max(outputs.data, 1)[1].cpu()
        run.log(name='Prediction Result', value=map_id_label[int(p_)])
    return map_id_label[int(p_)]


def predict_parallel(model, data_iter, map_id_label):
    model.eval()
    # for metrics
    # run = Run.get_context()
    results = []
    for batch_x, batch_y in data_iter:
        outputs = model(batch_x)
        p_ = torch.max(outputs.data, 1)[1].cpu().numpy()
        results.append(map_id_label[int(p_)])
    # run.log(name='Prediction Result', value=results)
    return results


def get_vocab(path_word_to_index):
    with open(path_word_to_index, 'r', encoding='utf-8') as f:
        w2i = json.load(f)
    return w2i


def get_id_label(path_label):
    map_id_label = {}
    map_label_id = {}
    with open(path_label, 'r', encoding='utf-8') as f:
        for i, label in enumerate(f.readlines()):
            label = label.rstrip()
            map_id_label[i] = label
            map_label_id[label] = i
    return map_id_label, map_label_id


def get_bigram_hash(text, index, ngram_size):
    word1 = text[index - 1] if index - 1 >= 0 else 0
    return (word1 * 10600202) % ngram_size


def get_trigram_hash(sequence, index, ngram_size):
    word1 = sequence[index - 1] if index - 1 >= 0 else 0
    word2 = sequence[index - 2] if index - 2 >= 0 else 0
    return (word2 * 10600202 * 13800202 + word1 * 10600202) % ngram_size


def load_dataset(file_path, word_to_index, map_label_id, max_len=32, ngram_size=200000):
    # [PAD]:0    [UNK]:1
    pad_id = word_to_index.get('[PAD]', 0)
    samples = []
    # load dataset for batch inference
    if isinstance(file_path, list):
        lines = []
        for file in file_path:
            with open(file, 'r', encoding='utf-8') as f:
                # 0 is the dummy label and doesn't work
                text = f.read().strip()
                if len(text) > 0:
                    lines.append(text + '\t' + '0')
    # load dataset for pipeline
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().split("\n")
            lines = [line.strip() for line in lines if len(line) > 0]
    for line in tqdm(lines, desc="load data"):
        line = line.split('\t')
        text = line[0].split(' ')
        label = line[1]
        # [UNK]:1
        text = ([word_to_index.get(word, 1) for word in text]) + [pad_id] * (max_len - len(text))
        text = text[:max_len]
        samples.append(process_data(text, label, max_len, ngram_size, map_label_id))
    return samples


def load_dataset_for_realtime_inference(input_sentence, word_to_index, map_label_id, max_len=32, ngram_size=200000):
    # 这里应该用jieba.cut()   这样就能同时处理中文和英文了
    import jieba
    input_sentence = jieba.lcut(input_sentence)
    input_sentence = list(filter(lambda x: x != ' ', input_sentence))
    pad_id = word_to_index.get('[PAD]', 0)
    text = ([word_to_index.get(word, 1) for word in input_sentence]) + [pad_id] * (max_len - len(input_sentence))
    text = text[:max_len]
    # 0 is the dummy label and doesn't work
    samples = [(process_data(text, '0', max_len, ngram_size, map_label_id))]
    return samples


def process_data(text: list, label: str, max_len=32, ngram_size=200000, map_label_id=None):
    bigram = []
    trigram = []
    id_ = None
    for i in range(max_len):
        bigram.append(get_bigram_hash(text, i, ngram_size))
        trigram.append(get_trigram_hash(text, i, ngram_size))
        # label not in map_label_id when inference
        id_ = map_label_id[label] if label in map_label_id else 0
    return (text, bigram, trigram, id_)


class DataIter(object):
    def __init__(self, samples, batch_size=32, shuffle=True, device=None):
        if shuffle:
            random.shuffle(samples)
        self.samples = samples
        self.batch_size = batch_size
        self.batch_num = len(samples) // self.batch_size
        self.residue = len(samples) % self.batch_num != 0
        self.index = 0
        self.device = device

    def _to_tensor(self, sub_samples: list):
        x = torch.LongTensor([sample[0] for sample in sub_samples]).to(self.device)
        bigram = torch.LongTensor([sample[1] for sample in sub_samples]).to(self.device)
        trigram = torch.LongTensor([sample[2] for sample in sub_samples]).to(self.device)
        y = torch.LongTensor([sample[3] for sample in sub_samples]).to(self.device)
        return (x, bigram, trigram), y

    def __next__(self):
        if self.index == self.batch_num and self.residue:
            sub_samples = self.samples[self.index * self.batch_size: len(self.samples)]
            self.index += 1
            return self._to_tensor(sub_samples)
        elif self.index >= self.batch_num:
            self.index = 0
            raise StopIteration
        else:
            sub_samples = self.samples[self.index * self.batch_size: (self.index + 1) * self.batch_size]
            self.index += 1
            return self._to_tensor(sub_samples)

    def __iter__(self):
        return self

    def __len__(self):
        if self.residue:
            return self.batch_num + 1
        else:
            return self.batch_num
