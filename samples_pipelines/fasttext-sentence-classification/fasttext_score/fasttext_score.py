import os
import sys
import json
import pandas as pd
from uuid import uuid4

import torch
from pathlib import Path
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl

from common.utils import DataIter, load_dataset, predict_parallel, get_vocab, get_id_label


@dsl.module(
    name="FastText Score",
    version='0.0.23',
    description='Predict the categories of the input sentences',
    job_type='parallel',
    parallel_inputs=[InputDirectory(name='Texts to score')],
    base_image='mcr.microsoft.com/azureml/intelmpi2018.3-cuda10.0-cudnn7-ubuntu16.04'
)
def fasttext_score(
        scored_data_output_dir: OutputDirectory(),
        fasttext_model_dir: InputDirectory() = '.'
):
    print('=====================================================')
    print(f'fasttext_model: {Path(fasttext_model_dir).resolve()}')
    print(f'scored_data_output_dir: {scored_data_output_dir}')
    path_word_to_index = os.path.join(fasttext_model_dir, 'word_to_index.json')
    word_to_index = get_vocab(path_word_to_index)
    path_label = os.path.join(fasttext_model_dir, 'label.txt')
    map_id_label, map_label_id = get_id_label(path_label)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('device:', device)
    path = os.path.join(fasttext_model_dir, 'shared_params.json')
    with open(path, 'r', encoding='utf-8') as f:
        shared_params = json.load(f)
    path = os.path.join(fasttext_model_dir, 'BestModel')
    model = torch.load(f=path, map_location=device)

    def run(files):
        if len(files) == 0:
            return []
        with torch.no_grad():
            test_samples = load_dataset(file_path=files, max_len=shared_params['max_len'],
                                        ngram_size=shared_params['ngram_size'], word_to_index=word_to_index,
                                        map_label_id=map_label_id)
            test_iter = DataIter(samples=test_samples, batch_size=1, shuffle=False, device=device)
            results = predict_parallel(model, test_iter, map_id_label)
            dict_ = {'Filename': files, 'Class': results}
            df = pd.DataFrame(data=dict_)
            output_file = os.path.join(scored_data_output_dir, f"{uuid4().hex}.parquet")
            df.to_parquet(output_file, index=False)
        return results

    return run


# This main code is only used for local debugging, will never be reached in AzureML when it is a parallel module.
# See https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-run-step#write-your-inference-script
if __name__ == '__main__':
    ModuleExecutor(fasttext_score).execute(sys.argv)
