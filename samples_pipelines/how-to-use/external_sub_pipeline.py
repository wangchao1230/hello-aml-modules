# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.core import Workspace
from azureml.pipeline.wrapper import Module, dsl

ws = Workspace.from_config()

execute_python_script_module = Module.load(ws, namespace='azureml', name='Execute Python Script')


@dsl.pipeline(name='external sub0 graph', description='sub0')
def external_sub_pipeline0(input):
    module1 = execute_python_script_module(
        # should be pipeline input
        dataset1=input,
    )
    module2 = execute_python_script_module(
        dataset1=module1.outputs.result_dataset,
    )
    return module2.outputs
