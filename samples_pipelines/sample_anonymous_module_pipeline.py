# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from azureml.core import Workspace, Dataset
from azureml.pipeline.wrapper import Pipeline, Module, dsl


# In[ ]:


ws = Workspace.from_config()
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep='\n')


# In[ ]:


# register anonymous modules
import os
from azureml.pipeline.wrapper._module_registration import _load_anonymous_module
local_module = _load_anonymous_module(ws, yaml_file=os.path.join('modules', 'hello_world', 'module_spec.yaml'))
github_yaml = "https://github.com/sherry1989/sample_modules/blob/master/3_basic_module/basic_module.yaml"
github_module = _load_anonymous_module(ws, yaml_file=github_yaml)
hello_world_module_id = local_module.module_version_id
basic_module_id = github_module.module_version_id


# In[ ]:


# get modules
hello_world_anonymous = Module.load(ws, id=hello_world_module_id)
basic_module_anonymous = Module.load(ws, id=basic_module_id)


# In[ ]:


# get dataset
from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path
automobile_price_data_raw = get_global_dataset_by_path(ws, 'automobile_price_data_raw', 'GenericCSV/Automobile_price_data_(Raw)')


# In[ ]:


# define pipeline
@dsl.pipeline(name='module_SDK_test Run 8575', description='test local module', default_compute_target='aml-compute')
def generated_pipeline():
    hello_world_anonymous_0 = hello_world_anonymous(
        input_path=automobile_price_data_raw,
        int_parameter='1',
        boolean_parameter='True',
        enum_parameter='option1',
        string_parameter='hello')
    hello_world_anonymous_0.runsettings.configure(target='aml-compute')
    
    basic_module_anonymous_0 = basic_module_anonymous(
        input_port=hello_world_anonymous_0.outputs.output_path,
        parameter_1='hello',
        parameter_2='1')
    basic_module_anonymous_0.runsettings.configure(target='aml-compute')


# In[ ]:


# create a pipeline
pipeline = generated_pipeline()


# In[ ]:


# validate pipeline and visualize the graph
pipeline.validate()


# In[ ]:


# submit a pipeline run
pipeline.submit(experiment_name='module_SDK_test').wait_for_completion()

