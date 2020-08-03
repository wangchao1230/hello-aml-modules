# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from azureml.core import Workspace, Dataset, Datastore
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


join_data_module_func = Module.load(ws, namespace='azureml', name='Join Data')
train_svd_recommender_module_func = Module.load(ws, namespace='azureml', name='Train SVD Recommender')

# datasets
input1 = Dataset.get_by_name(ws, 'query data (large)')
input2 = Dataset.get_by_name(ws, 'query data (small)')
global_datastore = Datastore(ws, name="azureml_globaldatasets")
movie_ratings_data = Dataset.File.from_files(global_datastore.path('GenericCSV/Movie_Ratings')).as_named_input('Movie_Ratings')
imdb_movie_titles_data = Dataset.File.from_files(global_datastore.path('GenericCSV/IMDB_Movie_Titles')).as_named_input('IMDB_Movie_Titles')


# In[ ]:


# steps
ejoin = ejoin_module_func().set_parameters(
    leftcolumns='m:query;querId',
    # missing 'rightcolumns' parameter
    leftkeys='m:query',
    rightkeys='m:Query',
    jointype='HashInner'
).set_inputs(
    left_input=input1,
    right_input=input2
)

eselect = eselect_module_func(
    # missing 'columns' parameter
    input=ejoin.outputs.ejoin_output
)

# pipeline
pipeline = Pipeline(nodes=[ejoin, eselect], outputs=eselect.outputs, default_compute_target="aml-compute")


# In[ ]:


graph = pipeline.validate()
graph


# In[ ]:


# Type mismatch & Invalid range
join_data = join_data_module_func(
    dataset1=movie_ratings_data,
    dataset2=imdb_movie_titles_data,
 comma_separated_case_sensitive_names_of_join_key_columns_for_l="{\"isFilter\":true,\"rules\":[{\"exclude\":false,\"ruleType\":\"ColumnNames\",\"columns\":[\"MovieId\"]}]}",
        comma_separated_case_sensitive_names_of_join_key_columns_for_r="{\"isFilter\":true,\"rules\":[{\"exclude\":false,\"ruleType\":\"ColumnNames\",\"columns\":[\"Movie ID\"]}]}",
    match_case="invalid",
    join_type="invalid",
    keep_right_key_columns_in_joined_table=101
)

train_svd = train_svd_recommender_module_func(
    training_dataset_of_user_item_rating_triples=movie_ratings_data,
    number_of_factors="0",
    number_of_recommendation_algorithm_iterations="0",
    learning_rate="10"
)

pipeline = Pipeline(nodes=[join_data, train_svd], default_compute_target="aml-compute")
graph = pipeline.validate()
graph

