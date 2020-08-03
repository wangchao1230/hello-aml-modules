# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
from azureml.core import Workspace, Dataset
from azureml.pipeline.wrapper import Module, dsl, Pipeline
from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path


# In[ ]:


ws = Workspace.from_config()
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')


# In[ ]:


# Module
execute_python_script_module = Module.load(ws, namespace='azureml', name='Execute Python Script')


# Dataset
global_input_data = get_global_dataset_by_path(ws, 'Automobile_price_data', 'GenericCSV/Automobile_price_data_(Raw)')


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


module1 = execute_python_script_module(
    dataset1=global_input_data,
)
module2 = execute_python_script_module(
    dataset1=module1.outputs.result_dataset,
)
pipeline1 = Pipeline(nodes=[module1, module2], outputs=module2.outputs, name="p1")

module3 = execute_python_script_module(
    dataset1=pipeline1.outputs.result_dataset,
)
module4 = execute_python_script_module(
    dataset1=module3.outputs.result_dataset,
)
pipeline2 = Pipeline(nodes=[module3, module4, pipeline1], outputs=module4.outputs, name="p2")

module5 = execute_python_script_module(
    dataset1=train_data,
    dataset2=pipeline2.outputs.result_dataset
)

pipeline = Pipeline(nodes=[module5, pipeline2], outputs=module5.outputs)


# In[ ]:


pipeline.validate()


# In[ ]:


run = pipeline.submit(
    experiment_name='sample_sub_pipeline_no_dsl'
)
run.wait_for_completion()

pipeline.save(
    experiment_name='sample_sub_pipeline_no_dsl'
)

