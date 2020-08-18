import os
import json

import torch
from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType

from common.utils import load_dataset_for_realtime_inference, DataIter, predict, get_vocab, get_id_label

def init():
    global model, word_to_index, map_label_id, map_id_label, device, shared_params
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('device:', device)
    model_dir = os.getenv('AZUREML_MODEL_DIR')
    # Model.register() will upload the parent directory, so we need to include this direcotry in the path of model_dir
    # The name of this parent directory is the output port name.
    model_dir = os.path.join(model_dir, os.listdir(model_dir)[0])
    path = os.path.join(model_dir, 'shared_params.json')
    with open(path, 'r', encoding='utf-8') as f:
        shared_params = json.load(f)
    path_word_to_index = os.path.join(model_dir, 'word_to_index.json')
    word_to_index = get_vocab(path_word_to_index)
    path_label = os.path.join(model_dir, 'label.txt')
    map_id_label, map_label_id = get_id_label(path_label)
    model_name = 'BestModel'
    model_path = os.path.join(model_dir, model_name)
    model = torch.load(f=model_path, map_location=device)


standard_sample_input = {'input_sentence': 'i want to travel around the world'}
standard_sample_output = {'category': 'dream'}


@input_schema('param', StandardPythonParameterType(standard_sample_input))
@output_schema(StandardPythonParameterType(standard_sample_output))
def run(param):
    with torch.no_grad():
        test_samples = load_dataset_for_realtime_inference(input_sentence=param['input_sentence'],
                                                           word_to_index=word_to_index, map_label_id=map_label_id,
                                                           max_len=shared_params['max_len'],
                                                           ngram_size=shared_params['ngram_size'])
        test_iter = DataIter(samples=test_samples, batch_size=1, shuffle=False, device=device)
        try:
            result = predict(model, test_iter, map_id_label)
            # You can return any data type, as long as it is JSON serializable.
            return result
        except Exception as e:
            error = str(e)
            return error
