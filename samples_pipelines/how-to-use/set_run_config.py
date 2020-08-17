# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from azureml.core import Workspace
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.pipeline.wrapper import Module, Pipeline


# In[ ]:


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
                   


# In[ ]:


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


# In[ ]:


test_pipeline = Pipeline(nodes=[mpi_train], name="test mpi", default_compute_target='aml-compute')


# In[ ]:


errors = test_pipeline.validate()


# In[ ]:


run = test_pipeline.submit(
    experiment_name='mpi_test',
)

run.wait_for_completion()


# In[ ]:


pipeline_draft = test_pipeline.save(
    experiment_name='module_SDK_mpi_test',
)
pipeline_draft

