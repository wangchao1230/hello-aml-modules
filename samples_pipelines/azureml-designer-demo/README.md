# azureml-designer-demo

#### Overview
In this repository, we customize some modules used on the Azure Machine Learning designer to reproduce the model of [fastText](https://arxiv.org/pdf/1607.01759.pdf). 
If you have access to [Visual Studio Codespaces](https://visualstudio.microsoft.com/services/visual-studio-codespaces/), then you do not need to install the development tools and configure the environment. Because, they will be prepared automatically. Refer to ``` .devcontainer/how-to-use-Dockerfile.md ``` for more details about how to build your own docker image use on Codespaces.

#### Module Description
1. ```split_data_txt``` process the input data for train, evaluation, and score

2. ```split_data_txt_for_parallel``` process the input data for train, evaluation, and score. This module organizes dataset according to demand of the parallel module

3. ```fasttext_train``` trains the fastText model with the training data and output the trained model.

4. ```fasttext_evaluation``` evaluates the performance of the trained model with the test data.

5. ```fasttext_score``` outputs the category of an input sentence with the trained model.

6. ```fasttext_score_parallel``` outputs the categories of many sentences with the trained model. It can enjoy the efficiency improvement brought by parallel computing.

7. ```compare_two_models``` compares the evaluation results of two trained models and saves the better one.



#### Demo Description

1. ```sample_fasttext_pipeline.ipynb``` contains two separate training processes and use the better trained model to predict the category of an input sentence.
2. ```sample_fasttext_pipeline_parallel.ipynb``` contains one training process and predict the categories of many sentences with the parallel module ``````fasttext_score_parallel``````.
3. ```sample_fasttext_deploy.ipynb``` first shows how to get the trained model from a completed experiment. Then, it demonstrates how to deploy the model with [Azure Container Instances](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-azure-container-instance), [Azure Machine Learning compute instance web service](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-local-container-notebook-vm), and [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-azure-kubernetes-service). Finally, it shows how to consume the deployed service.
