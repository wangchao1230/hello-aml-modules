import os
import sys
import random

from azureml.core import Run
from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, OutputDirectory, InputDirectory


@dsl.module(
    name="Split Data Txt For Parallel",
    version='0.0.13',
    description='Processing goal: text data set where each line of the file is a piece of data. This module divides\
    the data set into training set, verification set and test set. The test set is used for a parallel module.'
)
def split_data_txt_for_parallel(
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
    input_dir = os.path.join(input_dir, 'data.txt')
    with open(input_dir, 'r', encoding='utf-8') as f:
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
    os.makedirs(training_data_output, exist_ok=True)
    path = os.path.join(training_data_output, "data.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(train)
    print(path)
    print(os.listdir(training_data_output))

    os.makedirs(validation_data_output, exist_ok=True)
    path = os.path.join(validation_data_output, "data.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(dev)
    print(path)
    print(os.listdir(validation_data_output))

    os.makedirs(test_data_output, exist_ok=True)
    for i, line in enumerate(test):
        path_new = os.path.join(test_data_output, str(i))
        with open(path_new, 'w', encoding='utf-8') as f:
            f.write(line)
    print('============================================')


if __name__ == '__main__':
    ModuleExecutor(split_data_txt_for_parallel).execute(sys.argv)
