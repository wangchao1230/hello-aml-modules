# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import shutil
import sys
import os
from enum import Enum
from pathlib import Path

from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, OutputFile, OutputDirectory, InputFile, InputDirectory


class MyEnum(Enum):
    Enum0 = 'Enum0'
    Enum1 = 'Enum1'
    Enum2 = 'Enum2'

# If the name is not specified, the camel case of the function name is used.
# The docstring of the function is used as the description of the module.
@dsl.module()
def sample_module(
        # The input/output port are defined using the following 4 annotations.
        # Note that you need to register data type using
        # DataType.create_data_type(ws, 'MyDirectory', description=description, is_directory=True)
        # DataType.create_data_type(ws, 'MyFile', description=description, is_directory=False)
        # See https://docs.microsoft.com/en-us/python/api/azureml-pipeline-core/azureml.pipeline.core.graph.datatype?view=azure-ml-py#create-data-type-workspace--name--description--is-directory--parent-datatypes-none-
        output_dir: OutputDirectory(type='MyDirectory'),
        output_file: OutputFile(type='MyFile'),
        input_dir: InputDirectory(type='MyDirectory') = None,
        input_file: InputFile(type='MyFile') = None,
        # The parameter with default values will be considered as annotated with such type,
        # Now we support the following 5 types: str, int, float, bool, enum
        str_param='abc',
        int_param=1,
        float_param=0.1,
        bool_param=False,
        enum_param=MyEnum.Enum0,
        # If the default value is None without annotation, it will be treated as str.
        none_param=None,
):
    """A sample module use different parameter types and customized input/output ports."""
    print(f"Arg 'input_dir' = '{input_dir}', type='{type(input_dir)}'")
    if input_dir:
        print(f"Contents of input directory:")
        print('\n'.join(f.name for f in Path(input_dir).iterdir()))
    print(f"Arg 'input_file' = {input_file}, type='{type(input_file)}'")
    print(f"Arg 'output_dir' = {output_dir}, type='{type(output_dir)}'")
    print(f"Arg 'output_file' = {output_file}, type='{type(output_file)}'")
    print(f"Arg 'str_param' = {str_param}, type='{type(str_param)}'")
    print(f"Arg 'int_param' = {int_param}, type='{type(int_param)}'")
    print(f"Arg 'float_param' = {float_param}, type='{type(float_param)}'")
    print(f"Arg 'bool_param' = {bool_param}, type='{type(bool_param)}'")
    print(f"Arg 'enum_param' = {enum_param}, type='{type(enum_param)}'")
    print(f"Arg 'none_param' = {none_param}, type='{type(none_param)}'")

    data = str_param
    if input_file:
        with open(input_file, 'r') as fin:
            data = fin.read()
        print("Content of input file:", data)
    if input_dir:
        shutil.copytree(input_dir, output_dir)
    else:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "test.txt"), 'w') as fout:
            fout.write(data)
    with open(output_file, 'w') as fout:
        fout.write(data)


if __name__ == '__main__':
    ModuleExecutor(sample_module).execute(sys.argv)
