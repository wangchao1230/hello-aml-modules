# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# # Demo: Replace module in pipeline
# 
# ## step 0: Preparation - create a simple pipeline

# In[ ]:


import os

from azureml.core import Workspace, Dataset
from azureml.pipeline.wrapper import Module, Pipeline, dsl
from azureml.core.compute import AmlCompute, ComputeTarget
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
                                                                min_nodes = 1,
                                                                max_nodes = 4)
    aml_compute = ComputeTarget.create(workspace, aml_compute_target, provisioning_config)
    aml_compute.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)


# In[ ]:


# load datasets
github_yaml = "https://github.com/sherry1989/sample_modules/blob/master/3_basic_module/basic_module.yaml"
github_module = Module.from_yaml(workspace, yaml_file=github_yaml)
blob_input_data =     get_global_dataset_by_path(workspace,
                               'Automobile_price_data',
                               'GenericCSV/Automobile_price_data_(Raw)')

hello_world = Module.from_yaml(workspace, yaml_file=os.path.join(
                               'modules', 'hello_world', 'module_spec.yaml'))

hello_world_demo1 =     Module.from_yaml(workspace, yaml_file=os.path.join(
                               'modules', 'hello_world', 'module_replacement_demo1.yaml'))
hello_world_demo2 =     Module.from_yaml(workspace, yaml_file=os.path.join(
                               'modules', 'hello_world', 'module_replacement_demo2.yaml'))

@dsl.pipeline(name='test_module_replace_sub_pipeline', default_compute_target='aml-compute')
def test_module_replace_sub_pipeline(input_path):
    module1 = hello_world(
        input_path=input_path,
        string_parameter="hello",
        int_parameter=1,
        boolean_parameter=True,
        enum_parameter="option1"
    )
    return module1.outputs


@dsl.pipeline(name='test_module_replace_parent_pipeline', default_compute_target='aml-compute')
def test_module_replace_parent_pipeline():
    module1 = test_module_replace_sub_pipeline(blob_input_data)
    module2 = github_module(
        input_port=module1.outputs.output_path
    )
    return module2.outputs

@dsl.pipeline(name='test_module_replace_pipeline', default_compute_target='aml-compute')
def test_module_replace_pipeline():
    module1 = hello_world(
        input_path=blob_input_data,
        string_parameter="hello",
        int_parameter=1,
        boolean_parameter=True,
        enum_parameter="option1"
    )
    module2 = github_module(
        input_port=module1.outputs.output_path
    )
    return module2.outputs

pipeline = test_module_replace_pipeline()
pipeline.validate()


# ## Feature 1: Replace module by module function
# 
# * **replace origin module `hello_world` to `hello_world_demo1` which added an optional input port `Input path2`**

# In[ ]:


pipeline.replace(hello_world, hello_world_demo1)
pipeline.validate()


# ## *Feature 2: Do some checks to validate operation as much as possible*
# 
# * **try to replace origin module `hello_world` to `hello_world_demo2` which added a required input port `Input path3`**
# 
#     **this operation will be rejected*

# In[ ]:


pipeline = test_module_replace_pipeline()
pipeline.replace(hello_world, hello_world_demo2)


# ## *Feature 3: Allow user skip those checks mentioned before*
# 
# * **force replace origin module `hello_world` to `hello_world_demo2` which added a required input port `Input path3`**
# 
#     **this operation cause pipeline validate raise error*

# In[ ]:


pipeline = test_module_replace_pipeline()
pipeline.replace(hello_world, hello_world_demo2, force=True)
pipeline.validate()


# ## *Feature 4: Allow replace modules in sub-pipeline or not*
# 
# * **define a simple pipeline with sub-pipeline**

# In[ ]:


pipeline = test_module_replace_parent_pipeline()
pipeline.validate()


# * **regular replace with `recursive` default value False**
# 
#     **this operation won't make a difference*

# In[ ]:


pipeline.replace(hello_world, hello_world_demo1)
pipeline.validate()


# * **replace with `recursive=True`**
# 
#     **this operation will make a difference*

# In[ ]:


pipeline.replace(hello_world, hello_world_demo1, recursive=True)
pipeline.validate()

