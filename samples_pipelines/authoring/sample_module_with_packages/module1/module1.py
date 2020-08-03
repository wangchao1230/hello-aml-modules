# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys

from azureml.pipeline.wrapper.dsl.module import ModuleExecutor
from azureml.pipeline.wrapper import dsl

from package1.foo import bar


@dsl.module(
    name="Basic Module"
)
def basic_module(
    string_parameter: str,
    int_parameter: int,
    boolean_parameter: bool,
    string_parameter_with_default='abc',
):
    bar()


if __name__ == '__main__':
    ModuleExecutor(basic_module).execute(sys.argv)
