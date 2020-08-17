# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from azureml.core import Workspace, Run, Dataset, Datastore
from azureml.core.compute import AmlCompute
from azureml.pipeline.wrapper import Module, dsl

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


join_data_module_func = Module.load(ws, namespace='azureml', name='Join Data')
execute_python_script_module_func = Module.load(ws, namespace='azureml', name='Execute Python Script')
remove_duplicate_rows_module_func = Module.load(ws, namespace='azureml', name='Remove Duplicate Rows')
split_data_module_func = Module.load(ws, namespace='azureml', name='Split Data')
train_svd_recommender_module_func = Module.load(ws, namespace='azureml', name='Train SVD Recommender')
select_columns_module_func = Module.load(ws, namespace='azureml', name='Select Columns in Dataset')
score_svd_recommender_module_func = Module.load(ws, namespace='azureml', name='Score SVD Recommender')
evaluate_recommender_module_func = Module.load(ws, namespace='azureml', name='Evaluate Recommender')


# In[ ]:


global_datastore = Datastore(ws, name="azureml_globaldatasets")
movie_ratings_data = Dataset.File.from_files(global_datastore.path('GenericCSV/Movie_Ratings')).as_named_input('Movie_Ratings')
imdb_movie_titles_data = Dataset.File.from_files(global_datastore.path('GenericCSV/IMDB_Movie_Titles')).as_named_input('IMDB_Movie_Titles')


# In[ ]:


@dsl.pipeline(name='sample_pipeline', description='Sample 10: Recommendation - Movie Rating Tweets',  default_compute_target='aml-compute')
def sample_pipeline():
    join_data = join_data_module_func(
        dataset1=movie_ratings_data, 
        dataset2=imdb_movie_titles_data,
        comma_separated_case_sensitive_names_of_join_key_columns_for_l = "{\"isFilter\":true,\"rules\":[{\"exclude\":false,\"ruleType\":\"ColumnNames\",\"columns\":[\"MovieId\"]}]}",
        comma_separated_case_sensitive_names_of_join_key_columns_for_r = "{\"isFilter\":true,\"rules\":[{\"exclude\":false,\"ruleType\":\"ColumnNames\",\"columns\":[\"Movie ID\"]}]}",
        match_case="True",
        join_type="Inner Join",
        keep_right_key_columns_in_joined_table="True"
    )
    execute_python_script = execute_python_script_module_func(
        dataset1=join_data.outputs.results_dataset,
        python_script="\n# The script MUST contain a function named azureml_main\n# which is the entry point for this module.\n\n# imports up here can be used to\n\n# The entry point function can contain up to two input arguments:\n#   Param<dataframe1>: a pandas.DataFrame\n#   Param<dataframe2>: a pandas.DataFrame\ndef azureml_main(dataframe1 = None, dataframe2 = None): return dataframe1[['UserId','Movie Name','Rating']],"
    )
    remove_duplicate_rows = remove_duplicate_rows_module_func(
        dataset=execute_python_script.outputs.result_dataset,
        key_column_selection_filter_expression = "{\"isFilter\":true,\"rules\":[{\"exclude\":false,\"ruleType\":\"ColumnNames\",\"columns\":[\"Movie Name\",\"UserId\"]}]}",
        retain_first_duplicate_row = "True"
    )
    split_data = split_data_module_func(
        dataset=remove_duplicate_rows.outputs.results_dataset,
        splitting_mode = "Split Rows",
        fraction_of_rows_in_the_first_output_dataset="0.5",
        randomized_split="True",
        random_seed="0",
        stratified_split="False",
        stratification_key_column="" # this should be optional
    )
    train_svd = train_svd_recommender_module_func(
        training_dataset_of_user_item_rating_triples= split_data.outputs.results_dataset1,
        number_of_factors="200",
        number_of_recommendation_algorithm_iterations="30",
        learning_rate="0.005"
    )
    select_columns = select_columns_module_func(
        dataset= split_data.outputs.results_dataset2,
        select_columns= "{\"isFilter\":true,\"rules\":[{\"exclude\":false,\"ruleType\":\"ColumnNames\",\"columns\":[\"UserId\",\"Movie Name\"]}]}"
    )
    score_svd = score_svd_recommender_module_func(
        trained_svd_recommendation= train_svd.outputs.trained_svd_recommendation,
        dataset_to_score = select_columns.outputs.results_dataset,
        recommender_prediction_kind = "Rating Prediction",
        #Recommended_item_selection =""
        #Minimum_size_of_the_recommendation_pool_for_a_single_user="",
        #Maximum_number_of_items_to_recommend_to_a_user= "",
        #Whether_to_return_the_predicted_ratings_of_the_items_along_with_the_labels= ""
    )
    evaluate = evaluate_recommender_module_func(
        test_dataset=split_data.outputs.results_dataset2,
        scored_dataset= score_svd.outputs.scored_dataset
    )
    


# In[ ]:


pipeline = sample_pipeline()
pipeline.validate()


# In[ ]:


run = pipeline.submit(
    experiment_name='sample_builtin_module', tags = {"origin": "notebook"}
)


# In[ ]:


run.wait_for_completion()


# In[ ]:


run


# In[ ]:


draft = pipeline.save(
    experiment_name='sample_builtin_module'
)
#    default_compute_target='kubeflow-aks')
draft

