# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, OutputFile

from my_module import *
import my_module


@dsl.module()
def add(
    output_file: OutputFile(),
    a=1,
    b=2,
    c=3,
):
    return my_module.add(**locals())


if __name__ == '__main__':
    ModuleExecutor(add).execute(sys.argv)
