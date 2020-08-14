import os
import sys
import shutil
import random

from azureml.core import Run
from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, OutputDirectory, InputDirectory


@dsl.module(
    name="Split Data Txt",
    version='0.0.42',
    description='Processing objects: text format data set, each line of the text file is a piece of data, \
    this module divides the data set into training set, verification set and test set.'
)
def split_data_txt(
        training_data_output: OutputDirectory(),
        validation_data_output: OutputDirectory(),
        test_data_output: OutputDirectory(),
        input_dir: InputDirectory() = None,
        training_data_ratio=0.7,
        validation_data_ratio=0.1,
        random_split=False,
        seed=0
):
    # hardcode: data.txt
    print('============================================')
    print(f"value of input_dir:'{input_dir}', type of input_dir:'{type(input_dir)}'")
    path_input_data = os.path.join(input_dir, 'data.txt')
    with open(path_input_data, 'r', encoding='utf-8') as f:
        data = f.readlines()
    random.seed(seed if random_split else 0)
    random.shuffle(data)
    n = len(data)
    # for metrics
    run = Run.get_context()
    training_data_num = int(n * training_data_ratio)
    dev_data_num = int(n * validation_data_ratio)
    train = data[:training_data_num]
    dev = data[training_data_num:training_data_num + dev_data_num]
    test = data[training_data_num + dev_data_num:]
    print('num of total data:', len(data))
    print('num of training data:', len(train))
    print('num of validation data:', len(dev))
    print('num of test_data:', len(test))
    # for metrics
    run.log(name='num of total data', value=len(data))
    run.log(name='num of training data', value=len(train))
    run.log(name='num of validation data', value=len(dev))
    run.log(name='num of test_data', value=len(test))
    path_label = os.path.join(input_dir, 'label.txt')
    path_word_to_index = os.path.join(input_dir, 'word_to_index.json')

    # os.makedirs(training_data_output, exist_ok=True)
    shutil.copy(src=path_label, dst=training_data_output)
    shutil.copy(src=path_word_to_index, dst=training_data_output)
    path = os.path.join(training_data_output, "data.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(train)

    shutil.copy(src=path_label, dst=validation_data_output)
    shutil.copy(src=path_word_to_index, dst=validation_data_output)
    # os.makedirs(validation_data_output, exist_ok=True)
    path = os.path.join(validation_data_output, "data.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(dev)

    shutil.copy(src=path_label, dst=test_data_output)
    shutil.copy(src=path_word_to_index, dst=test_data_output)
    # os.makedirs(test_data_output, exist_ok=True)
    path = os.path.join(test_data_output, "data.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(test)
    print('============================================')


if __name__ == '__main__':
    ModuleExecutor(split_data_txt).execute(sys.argv)
