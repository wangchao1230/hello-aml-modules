import os
import sys
import json
import shutil
from pathlib import Path

from azureml.core import Run
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl


@dsl.module(
    name="Compare Two Models",
    version="0.0.18",
    description="Choose the better model according to accuracy"
)
def compare_two_models(
        the_better_model: OutputDirectory(),
        first_trained_model: InputDirectory() = None,
        first_trained_result: InputDirectory() = None,
        second_trained_model: InputDirectory() = None,
        second_trained_result: InputDirectory() = None
):
    # hardcode: result.json and BestModel
    print('=====================================================')
    print(f'input_dir: {Path(first_trained_model).resolve()}')
    print(f'input_dir: {Path(first_trained_result).resolve()}')
    print(f'input_dir: {Path(second_trained_model).resolve()}')
    print(f'input_dir: {Path(second_trained_result).resolve()}')
    # for metrics
    run = Run.get_context()
    path = os.path.join(first_trained_result, 'result.json')
    result_first = json.load(open(path, 'r'))['acc']
    path = os.path.join(second_trained_result, 'result.json')
    second_first = json.load(open(path, 'r'))['acc']
    dst = the_better_model
    if result_first >= second_first:
        print('choose the first model')
        run.log(name='which one', value='first')
        src = os.path.join(first_trained_model, 'BestModel')
        shutil.copy(src=src, dst=dst)
    else:
        print('choose the second model')
        run.log(name='which one', value='second')
        src = os.path.join(second_trained_model, 'BestModel')
        shutil.copy(src=src, dst=dst)
    path_word_to_index = os.path.join(first_trained_model, 'word_to_index.json')
    path_label = os.path.join(first_trained_model, 'label.txt')
    shutil.copy(src=path_word_to_index, dst=dst)
    shutil.copy(src=path_label, dst=dst)
    print('=====================================================')


if __name__ == '__main__':
    ModuleExecutor(compare_two_models).execute(sys.argv)
