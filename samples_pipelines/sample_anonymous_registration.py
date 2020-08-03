# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from azureml.core import Workspace
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.pipeline.wrapper import Module, Pipeline
from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path

workspace = Workspace.from_config()
print(workspace.name, workspace.resource_group, workspace.location, workspace.subscription_id, sep = '\n')

aml_compute_target = "aml-compute"
try:
    aml_compute = AmlCompute(workspace, aml_compute_target)
    print("Found existing compute target: {}".format(aml_compute_target))
except:
    print("Creating new compute target: {}".format(aml_compute_target))
    
    provisioning_config = AmlCompute.provisioning_configuration(vm_size = "STANDARD_D2_V2",
                                                                min_nodes = 0, 
                                                                max_nodes = 4)    
    aml_compute = ComputeTarget.create(workspace, aml_compute_target, provisioning_config)
    aml_compute.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)


# In[ ]:


# load modules
local_module = Module.from_yaml(workspace, yaml_file=os.path.join('modules', 'hello_world', 'module_spec.yaml'))
github_yaml = "https://github.com/sherry1989/sample_modules/blob/master/3_basic_module/basic_module.yaml"
github_module = Module.from_yaml(workspace, yaml_file=github_yaml)


# In[ ]:


# load datasets
blob_input_data = get_global_dataset_by_path(workspace, 'Automobile_price_data', 'GenericCSV/Automobile_price_data_(Raw)')


# In[ ]:


module1 = local_module(
    input_path=blob_input_data,
    string_parameter= "hello",
    int_parameter= 1,
    boolean_parameter = True,
    enum_parameter="option1"
)
module2 = github_module(
    input_port=module1.outputs.output_path
)

test_pipeline = Pipeline(nodes=[module1, module2], outputs=module2.outputs, name="test local module",
                         default_compute_target='aml-compute')


# In[ ]:


errors = test_pipeline.validate()


# In[ ]:


run = test_pipeline.submit(
    experiment_name='module_SDK_test',
)

run.wait_for_completion()


# In[ ]:


pipeline_draft = test_pipeline.save(
    experiment_name='module_SDK_local_module_test',
)
pipeline_draft

