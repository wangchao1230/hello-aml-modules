# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from azureml.core import Workspace
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.pipeline.wrapper import Module, Pipeline
workspace = Workspace.from_config()
print(workspace.name, workspace.resource_group, workspace.location, workspace.subscription_id, sep='\n')

aml_compute_target = "aml-compute"
try:
    aml_compute = AmlCompute(workspace, aml_compute_target)
    print("Found existing compute target: {}".format(aml_compute_target))
except:
    print("Creating new compute target: {}".format(aml_compute_target))
    
    provisioning_config = AmlCompute.provisioning_configuration(vm_size = "STANDARD_D2_V2",
                                                                min_nodes = 1, 
                                                                max_nodes = 4)    
    aml_compute = ComputeTarget.create(workspace, aml_compute_target, provisioning_config)
    aml_compute.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)

try:
    mpi_train_module_func = Module.load(workspace, namespace="microsoft.com/azureml/samples", name="Hello World MPI Job")
except:
    mpi_train_module_func = Module.register(workspace, os.path.join('modules', 'mpi_module', 'module_spec.yaml'))

from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path
blob_input_data = get_global_dataset_by_path(workspace, 'Automobile_price_data', 'GenericCSV/Automobile_price_data_(Raw)')

mpi_train = mpi_train_module_func(input_path = blob_input_data, string_parameter = "test1")
mpi_train.runsettings.configure(node_count=2, process_count_per_node=2)

print(mpi_train.runsettings.node_count)
mpi_train.runsettings.node_count = 1

test_pipeline = Pipeline(nodes=[mpi_train], name="test mpi", default_compute_target='aml-compute')
test_pipeline.validate()


# In[ ]:


import json
from azureml.core import Workspace, Dataset
from azureml.pipeline.wrapper import Module, dsl
from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path
from external_sub_pipeline import external_sub_pipeline0

ws = Workspace.from_config()
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')

# Module
execute_python_script_module = Module.load(ws, namespace='azureml', name='Execute Python Script')


# TODO: Dataset
blob_input_data = get_global_dataset_by_path(ws, 'Automobile_price_data', 'GenericCSV/Automobile_price_data_(Raw)')

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
    @dsl.pipeline(name='internal sub graph', description='internal sub')
    def sub_pipeline_internal(input):
        module1 = execute_python_script_module(
            # should be pipeline input
            dataset1=input,
        )
        module2 = execute_python_script_module(
            dataset1=module1.outputs.result_dataset,
        )
        return module2.outputs

    sub0 = sub_pipeline_internal(blob_input_data)
    sub1 = sub_pipeline1(sub0.outputs.result_dataset)
    sub2 = sub_pipeline2(sub1.outputs.result_dataset)
    module2 = execute_python_script_module(
        dataset1=sub2.outputs.result_dataset,
        dataset2=train_data,
    )

    external = external_sub_pipeline0(sub1.outputs.result_dataset)
    return module2.outputs

pipeline1 = parent_pipeline()
pipeline1.validate()


# In[ ]:


pipeline1.diff(test_pipeline)


# In[ ]:


test_pipeline.diff(pipeline1)

