# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from azureml.core import Workspace, Datastore, Dataset
from azureml.pipeline.wrapper import Module, dsl
from azureml.pipeline.wrapper._dataset import get_global_dataset_by_path
from azureml.core.compute import AmlCompute, ComputeTarget


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


# Module
select_columns_in_dataset = Module.load(ws, namespace='azureml', name='Select Columns in Dataset')
clean_missing_data = Module.load(ws, namespace='azureml', name='Clean Missing Data')
split_data = Module.load(ws, namespace='azureml', name='Split Data')
join_data = Module.load(ws, namespace='azureml', name='Join Data')


# Dataset
try:
    dset = Dataset.get_by_name(ws, 'Automobile_price_data_(Raw)')
except Exception:
    global_datastore = Datastore(ws, name="azureml_globaldatasets")
    dset = Dataset.File.from_files(global_datastore.path('GenericCSV/Automobile_price_data_(Raw)'))
    dset.register(workspace=ws,
                  name='Automobile_price_data_(Raw)',
                  create_new_version=True)
blob_input_data = dset


# In[ ]:


# sub pipeline: TODO improve this experience
@dsl.pipeline(name='sub sub', description='sub')
def sub_sub_pipeline(minimum_missing_value_ratio):
    module1 = select_columns_in_dataset(
        dataset=blob_input_data,
        select_columns="{\"isFilter\":true,\"rules\":[{\"exclude\":false,\"ruleType\":\"AllColumns\"},"
                       "{\"exclude\":true,\"ruleType\":\"ColumnNames\",\"columns\":[\"normalized-losses\"]}]}"
    )
    module2 = clean_missing_data(
        dataset=module1.outputs.results_dataset,
        columns_to_be_cleaned="{\"isFilter\":true,\"rules\":[{\"ruleType\":\"AllColumns\",\"exclude\":false}]}",
        cleaning_mode='Remove entire row',
        minimum_missing_value_ratio=minimum_missing_value_ratio
    )
    return module2.outputs

@dsl.pipeline(name='sub', description='sub', default_compute_target='aml-compute')
def sub_pipeline(random_seed, minimum_missing_value_ratio):
    sub_sub_pipeline1 = sub_sub_pipeline(minimum_missing_value_ratio)
    module3 = split_data(
        dataset=sub_sub_pipeline1.outputs.cleaned_dataset,
        splitting_mode='Split Rows',
        randomized_split='True',
        stratified_split='False',
        random_seed=random_seed
    )
    return module3.outputs

@dsl.pipeline(name='parent', description='parent', default_compute_target='aml-compute')
def test_pipeline():
    # the sub pipeline's param won't be parsed into pipeline parameter
    sub_pipeline1 = sub_pipeline('0', 0.0)
    sub_pipeline2 = sub_pipeline('0', 0.0)
    module4 = join_data(
        dataset1=sub_pipeline1.outputs.results_dataset1,
        dataset2=sub_pipeline2.outputs.results_dataset1,
        comma_separated_case_sensitive_names_of_join_key_columns_for_l='%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22'
                                                                       'exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%5D%7D',
        comma_separated_case_sensitive_names_of_join_key_columns_for_r='%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22'
                                                                       'exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%5D%7D',
    )
    return module4.outputs

# pipeline's param will be parsed into pipeline parameter
pipeline1 = sub_pipeline('0', 0.0)
pipeline2 = test_pipeline()


# In[ ]:


pipelines = [pipeline1, pipeline2]

for pipeline in pipelines:
    run = pipeline.submit(
        experiment_name='module_SDK_pipeline_parameter_test'
    )
    run.wait_for_completion()
    pipeline.save(
        experiment_name='module_SDK_pipeline_parameter_test'
    )


# In[ ]:


pipeline2.outputs

