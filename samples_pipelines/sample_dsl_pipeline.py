# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from azureml.core import Workspace, Dataset
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.pipeline.wrapper import Module, dsl

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


try:
    train_module_func = Module.load(ws, namespace='microsoft.com/aml/samples', name='Train')
except:
    train_module_func = Module.register(ws, os.path.join('modules', 'train-score-eval', 'train.yaml'))

try:
    score_module_func = Module.load(ws, namespace='microsoft.com/aml/samples', name='Score')
except:
    score_module_func = Module.register(ws, os.path.join('modules', 'train-score-eval', 'score.yaml'))

try:
    eval_module_func = Module.load(ws, namespace='microsoft.com/aml/samples', name='Evaluate')
except:
    eval_module_func = Module.register(ws, os.path.join('modules', 'train-score-eval', 'eval.yaml'))
    
try:
    compare_module_func = Module.load(ws, namespace='microsoft.com/aml/samples', name='Compare 2 Models')    
except:
    compare_module_func = Module.register(ws, os.path.join('modules', 'train-score-eval', 'compare2.yaml'))

training_data_name = "Titanic"
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

train_data = Dataset.get_by_name(ws, training_data_name)
test_data = Dataset.get_by_name(ws, training_data_name)


# In[ ]:


@dsl.pipeline(name='training_pipeline', description='A sub pipeline including train/score/eval', default_compute_target='aml-compute')
def training_pipeline(learning_rate, train_dataset):
    train = train_module_func(
        training_data=train_dataset,
        max_epochs=5,
        learning_rate=learning_rate)
    train.runsettings.process_count_per_node = 2
    train.runsettings.node_count = 2

    score = score_module_func(
        model_input=train.outputs.model_output,
        test_data=test_data)
    eval = eval_module_func(scoring_result=score.outputs.score_output)

    return {**eval.outputs, **train.outputs}


@dsl.pipeline(name='dummy_automl_pipeline', description='A dummy pipeline that trains two models and output the better one', default_compute_target='aml-compute')
def dummy_automl_pipeline(train_dataset):
    train_and_evalute_model1 = training_pipeline(0.01, train_dataset)
    train_and_evalute_model2 = training_pipeline(0.02, train_dataset)
    train_and_evalute_model3 = training_pipeline(0.03, train_dataset)
    train_and_evalute_model4 = training_pipeline(0.04, train_dataset)

    compare12 = compare_module_func(
        model1=train_and_evalute_model1.outputs.model_output,
        eval_result1=train_and_evalute_model1.outputs.eval_output,
        model2=train_and_evalute_model2.outputs.model_output,
        eval_result2=train_and_evalute_model2.outputs.eval_output
    )
    compare34 = compare_module_func(
        model1=train_and_evalute_model3.outputs.model_output,
        eval_result1=train_and_evalute_model3.outputs.eval_output,
        model2=train_and_evalute_model4.outputs.model_output,
        eval_result2=train_and_evalute_model4.outputs.eval_output
    )

    compare = compare_module_func(
        model1=compare12.outputs.best_model,
        eval_result1=compare12.outputs.best_result,
        model2=compare34.outputs.best_model,
        eval_result2=compare34.outputs.best_result
    )
    return compare.outputs


# In[ ]:


pipeline = dummy_automl_pipeline(train_data)


# In[ ]:


pipeline.validate()


# In[ ]:


run = pipeline.submit(
    experiment_name='sample-pipelines'
)
run.wait_for_completion()
run


# In[ ]:


pipeline.save(
    experiment_name='sample-pipelines'
)

