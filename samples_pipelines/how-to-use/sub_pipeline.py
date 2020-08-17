# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import json
from azureml.core import Workspace, Dataset
from azureml.pipeline.wrapper import Module, dsl
from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path
from external_sub_pipeline import external_sub_pipeline0


# In[ ]:


ws = Workspace.from_config()
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')


# In[ ]:


# Module
execute_python_script_module = Module.load(ws, namespace='azureml', name='Execute Python Script')

# Basic Module
basic_yaml_file = os.path.join('modules', 'hello_world', 'module_spec.yaml')
basic_module_func = Module.from_yaml(ws, basic_yaml_file)

# MPI Module
mpi_yaml_file = os.path.join('modules', 'mpi_module', 'module_spec.yaml')
mpi_module_func = Module.from_yaml(ws, mpi_yaml_file)

# Parallel Module
parallel_yaml_file = os.path.join('modules', 'parallel_module', 'copy_files.yaml')
parallel_module_func = Module.from_yaml(ws, parallel_yaml_file)

# TODO: Dataset
blob_input_data = get_global_dataset_by_path(ws, 'Automobile_price_data', 'GenericCSV/Automobile_price_data_(Raw)')

# In[ ]:


training_data_name = 'aml_module_training_data'

if training_data_name not in ws.datasets:
    print('Registering a training dataset for sample pipeline ...')
    train_data = Dataset.File.from_files(path=['https://dprepdata.blob.core.windows.net/demo/Titanic.csv'])
    train_data.register(workspace=ws,
                        name=training_data_name,
                        description='Training data (just for illustrative purpose)')
    print('Registerd')
else:
    train_data = ws.datasets[training_data_name]
    print('Training dataset found in workspace')


# In[ ]:


@dsl.pipeline(name='sub0 graph', description='sub0')
def sub_pipeline0(input):
    module1 = execute_python_script_module(
        # should be pipeline input
        dataset1=input,
    )
    module2 = execute_python_script_module(
        dataset1=module1.outputs.result_dataset,
    )
    return module2.outputs


@dsl.pipeline(name='sub1 graph', description='sub1')
def sub_pipeline1(input):
    module1 = execute_python_script_module(
        dataset1=input
    )
    sub0 = sub_pipeline0(module1.outputs.result_dataset)
    return sub0.outputs


@dsl.pipeline(name='sub2 graph', description='sub1')
def sub_pipeline2(input):
    module1 = execute_python_script_module(
        dataset1=input
    )
    module2 = execute_python_script_module(
        dataset1=module1.outputs.result_dataset,
        dataset2=blob_input_data
    )
    module3 = execute_python_script_module(
        dataset1=input,
        dataset2=module2.outputs.result_dataset
    )
    module4 = execute_python_script_module(
        dataset1=train_data,
        dataset2=module3.outputs.result_dataset
    )
    sub0 = sub_pipeline0(module4.outputs.result_dataset)
    return sub0.outputs


@dsl.pipeline(name='parent graph', description='parent', default_compute_target="aml-compute")
def parent_pipeline():
    @dsl.pipeline(name='different type module', description='different type module', default_compute_target="aml-compute")
    def diff_type_pipeline(input, str_param, int_param, bool_param, enun_param):
        basic_module = basic_module_func(
            input_path=input,
            string_parameter= str_param,
            int_parameter= int_param,
            boolean_parameter = bool_param,
            enum_parameter=enun_param
        )

        # mpi module
        mpi_module = mpi_module_func(
            input_path=basic_module.outputs.output_path,
            string_parameter= str_param,
            int_parameter= int_param,
            boolean_parameter = bool_param,
            enum_parameter=enun_param
        )
        mpi_module.runsettings.configure(process_count_per_node=3, node_count=2)

        # parallel module
        parallel_module = parallel_module_func(
            input_folder=mpi_module.outputs.output_path
        )
        return mpi_module.outputs

    sub0 = diff_type_pipeline(blob_input_data, 'str_param', 10, True, "option2")
    sub1 = sub_pipeline1(sub0.outputs.output_path)
    sub2 = sub_pipeline2(sub1.outputs.result_dataset)
    module2 = execute_python_script_module(
        dataset1=sub2.outputs.result_dataset,
        dataset2=train_data,
    )

    external = external_sub_pipeline0(sub1.outputs.result_dataset)
    return module2.outputs



# In[ ]:


pipeline1 = parent_pipeline()
pipeline1.validate()

run = pipeline1.submit(
    experiment_name='module_SDK_test'
)
run.wait_for_completion()

pipeline1.save(
    experiment_name='module_SDK_test'
)


# In[ ]:


pipeline1 = parent_pipeline()

run = pipeline1.run(
    experiment_name='module_SDK_test', show_output=True, show_graph=True
)
run
