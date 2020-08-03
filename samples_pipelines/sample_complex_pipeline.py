# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json, os
from datetime import datetime
from azureml.core import Workspace, Dataset
from azureml.pipeline.wrapper import Module, dsl
from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path


# In[ ]:


ws = Workspace.from_config()
#ws = Workspace.get(name='itp-pilot', subscription_id='4aaa645c-5ae2-4ae9-a17a-84b9023bc56a', resource_group='itp-pilot-ResGrp')
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')


# In[ ]:


# Module
modulefunc = Module.from_yaml(ws, yaml_file=os.path.join('modules', 'noop', '1in2out.spec.yaml'))

# Dataset
data = get_global_dataset_by_path(ws, 'Automobile_price_data', 'GenericCSV/Automobile_price_data_(Raw)')


# In[ ]:


@dsl.pipeline(
    name='A huge pipeline composed with nodes 1 in 2 outs',
    description='A sample',
    default_compute_target='aml-compute'  # 'k80-16-a'
)
def cell_division():
    layer = 6
    nodes = []
    nodes.append(modulefunc(input1=data))
    for i in range(0, layer-1):
        print('i=', i, ' nodes len=', len(nodes))
        current_layer_nodes = []
        for j in range(0, pow(2, i)):
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\tj=', j)
            n = nodes[-j-1]
            current_layer_nodes.append(modulefunc(input1=n.outputs.output1))
            current_layer_nodes.append(modulefunc(input1=n.outputs.output2))
        nodes = nodes + current_layer_nodes

    return {**nodes[-1].outputs}


# In[ ]:


pipeline = cell_division()
pipeline.validate()


# In[ ]:


print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\t submitting')
run = pipeline.submit(
    experiment_name='module_SDK_test'
)
print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\t submitted')


# In[ ]:


#run.wait_for_completion()
run


# In[ ]:


print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\t saving')
draft = pipeline.save(
    experiment_name='module_SDK_test'
)
print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\t saved')
draft


# In[ ]:




