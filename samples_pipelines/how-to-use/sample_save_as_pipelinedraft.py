# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from azureml.core import Workspace, Dataset
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.pipeline.wrapper import Module, Pipeline


# In[ ]:


ws = Workspace.from_config()
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')

aml_compute_target = "aml-compute"
try:
    aml_compute = AmlCompute(ws, aml_compute_target)
    print("Found existing compute target: {}".format(aml_compute_target))
except:
    print("Creating new compute target: {}".format(aml_compute_target))

    provisioning_config = AmlCompute.provisioning_configuration(vm_size="STANDARD_D2_V2",
                                                                min_nodes=1,
                                                                max_nodes=4)    
    aml_compute = ComputeTarget.create(ws, aml_compute_target, provisioning_config)
    aml_compute.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)


# In[ ]:


# modules
try:
    ejoin_module_func = Module.load(ws, namespace='microsoft.com/bing', name='ejoin')
    eselect_module_func = Module.load(ws, namespace='microsoft.com/bing', name='eselect')
except:
    ejoin_module_func = Module.register(ws, os.path.join('modules', 'ejoin', 'amlmodule.yaml'))
    eselect_module_func = Module.register(ws, os.path.join('modules', 'eselect', 'amlmodule.yaml'))
# datasets
left_data_name = "left.tsv"
if left_data_name not in ws.datasets:
    print('Registering a training dataset for sample pipeline ...')
    left_data = Dataset.File.from_files(path=['https://desginerdemo.blob.core.windows.net/demo/left.tsv'])
    left_data.register(workspace = ws, name = left_data_name)
    print('Registerd')
else:
    left_data = ws.datasets[left_data_name]
    print('Training dataset found in workspace')

right_data_name = "right.tsv"
if right_data_name not in ws.datasets:
    print('Registering a training dataset for sample pipeline ...')
    right_data = Dataset.File.from_files(path=['https://desginerdemo.blob.core.windows.net/demo/right.tsv'])
    right_data.register(workspace = ws, name = right_data_name)
    print('Registerd')
else:
    right_data = ws.datasets[right_data_name]
    print('Training dataset found in workspace')

# datasets
input1 = Dataset.get_by_name(ws, left_data_name)
input2 = Dataset.get_by_name(ws, right_data_name)


# In[ ]:


# steps
ejoin = ejoin_module_func().set_parameters(
    leftcolumns='m:query;querId',
    rightcolumns='Market',
    leftkeys='m:query',
    rightkeys='m:Query',
    jointype='HashInner'
).set_inputs(
    left_input=input1,
    right_input=input2
)

eselect = eselect_module_func(
    columns='m:query;Market',
    input=ejoin.outputs.ejoin_output
)

# pipeline
pipeline = Pipeline(nodes=[ejoin, eselect], outputs=eselect.outputs, name='module sdk test draft', default_compute_target='aml-compute')


# In[ ]:


# Graph/module validation and visualization with .validate() function
# pipeline.validate() #TODO


# In[ ]:


run = pipeline.submit(
    experiment_name='module_SDK_test'
)
run.wait_for_completion()

pipeline_draft = pipeline.save(
    experiment_name='module_SDK_test',
    tags={'Sample':'Save as pipelineDraft'},
    properties={'Custom property':'Custom property value'}
)
pipeline_draft

