# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
from pathlib import Path
import shutil

from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl


@dsl.module(
    name="copy_files"
)
def copy_files(
        output_dir: OutputDirectory(),
        input_dir: InputDirectory() = '.',
        str_param='some_string',
):
    input_dir = Path(input_dir)
    print(f'input_dir: {input_dir.resolve()}')
    print(f'str_param: {str_param}')

    files = []
    if input_dir.is_dir():
        files = [str(f) for f in input_dir.iterdir()]

    if(len(files) == 0):
        raise ValueError(f'input_dir should be an directory with files')

    output_dir = Path(output_dir)
    with open(output_dir / f"output.txt", 'w') as fout:
        fout.write(str_param)


if __name__ == '__main__':
    ModuleExecutor(copy_files).execute(sys.argv)
