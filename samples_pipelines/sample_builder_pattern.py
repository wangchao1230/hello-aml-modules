# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Initialization Steps
from azureml.core import Workspace, Dataset, Datastore
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.pipeline.wrapper import Module, Pipeline

ws = Workspace.from_config()
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep = '\n')

aml_compute_target = "aml-compute"
try:
    aml_compute = AmlCompute(ws, aml_compute_target)
    print("Found existing compute target: {}".format(aml_compute_target))
except:
    print("Creating new compute target: {}".format(aml_compute_target))
    
    provisioning_config = AmlCompute.provisioning_configuration(vm_size = "STANDARD_D2_V2",
                                                                min_nodes = 1, 
                                                                max_nodes = 4)    
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
    
training_data_name = "Titanic.tsv"
if training_data_name not in ws.datasets:
    print('Registering a training dataset for sample pipeline ...')
    train_data = Dataset.File.from_files(path=['https://desginerdemo.blob.core.windows.net/demo/titanic.tsv'])
    train_data.register(workspace = ws, 
                              name = training_data_name, 
                              description = 'Training data (just for illustrative purpose)')
    print('Registerd')
else:
    train_data = ws.datasets[training_data_name]
    print('Training dataset found in workspace')

# datasets
input1 = Dataset.get_by_name(ws, training_data_name)
input2 = Dataset.get_by_name(ws, training_data_name)


# The created module provide builder style functions to help user change module setting.
# - set_parameters
# - set_inputs
# - inputs.configure
# - outputs.configure
# - runsettings.configure
# 
# There function also has dynamic generated signature. For exmaple: Press shift-tab in Jupyter will get:
# 
#  ![Signature](docs/jupyter_signature_set_parameters.jpg)
# 
# There is known issue with intellisense in VsCode.

# In[ ]:


import inspect

ejoin = ejoin_module_func()
# module function has dynamic generated signature
print(inspect.signature(ejoin.set_parameters))

# use shift-tab to show signature, tab to auto-completion. This works in jupyter but has some issue in Vscode.
ejoin.set_parameters()


# In[ ]:


# builder pattern to build module step
ejoin = ejoin_module_func().set_parameters(
    leftcolumns='Survived;Pclass;Name',
    rightcolumns='Sex;Age;SibSp;Parch;Ticket;Fare;Cabin;Embarked',
    leftkeys='PassengerId',
    rightkeys='PassengerId',
    jointype='HashInner'
).set_inputs(
    left_input=input1,
    right_input=input2
)

# Configure inputs
ejoin.inputs.leftinput.configure(mode='mount')
print(ejoin.inputs.leftinput.mode)

# Configure outputs
ejoin.outputs.ejoin_output.configure(output_mode='mount', datastore=Datastore(ws, name="myownblob"))

print(ejoin.outputs.ejoin_output.output_mode)
print(ejoin.outputs.ejoin_output.datastore.name)

eselect = eselect_module_func(
    columns='Survived;Name;Sex;Age',
    input=ejoin.outputs.ejoin_output
)

# pipeline
pipeline = Pipeline(nodes=[ejoin, eselect], outputs=eselect.outputs, default_compute_target='aml-compute')


# In[ ]:


pipeline.validate()


# In[ ]:


run = pipeline.submit(
    experiment_name='module_SDK_test',
)

run.wait_for_completion()

pipeline.save(
    experiment_name='module_SDK_test'
)

