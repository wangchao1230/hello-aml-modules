import os
import sys
import pandas as pd
from uuid import uuid4

import torch
from pathlib import Path
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl
from common.utils import load_dataset_parallel, DataIter_Parallel, predict_parallel, get_vocab, get_id_label


@dsl.module(
    name="FastText Score",
    version='0.0.22',
    description='Predict the categories of the input sentences',
    job_type='parallel',
    parallel_inputs=[InputDirectory(name='Texts to score')]
)
def fasttext_score(
        scored_data_output_dir: OutputDirectory(),
        fasttext_model_dir: InputDirectory() = '.',
):
    print('=====================================================')
    print(f'fasttext_model: {Path(fasttext_model_dir).resolve()}')
    print(f'scored_data_output_dir: {scored_data_output_dir}')
    path_word_to_index = os.path.join(fasttext_model_dir, 'word_to_index.json')
    word_to_index = get_vocab(path_word_to_index)
    path_label = os.path.join(fasttext_model_dir, 'label.txt')
    map_id_label, map_label_id = get_id_label(path_label)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    max_len_ = 32
    path = os.path.join(fasttext_model_dir, 'BestModel')
    model = torch.load(f=path)

    def run(files):
        if len(files) == 0:
            return []

        with torch.no_grad():
            test_samples = load_dataset_parallel(files=files, max_len=max_len_, word_to_index=word_to_index)
            test_iter = DataIter_Parallel(test_samples, shuffle=False)
            results = predict_parallel(model, test_iter, device, map_id_label)
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
