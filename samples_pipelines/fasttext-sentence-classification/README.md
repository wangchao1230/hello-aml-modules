<!-- #region -->
# fasttext-sentence-classification

#### Overview
In this repository, we customize some modules used on the Azure Machine Learning designer to reproduce the algorithm of [fastText](https://arxiv.org/pdf/1607.01759.pdf). 
If you have access to [Visual Studio Codespaces](https://visualstudio.microsoft.com/services/visual-studio-codespaces/), then you do not need to install the development tools and configure the environment. They will be prepared automatically. 

#### Module Description
1. ```split_data_txt``` divides the dataset into three parts: training, evaluation, and scoring

3. ```fasttext_train``` trains the fastText model with the training data and outputs the trained model.

4. ```fasttext_evaluation``` evaluates the performance of the trained model with the test data.

5. ```fasttext_score``` outputs the categories of lots of sentences with the trained model. With this module, you could enjoy the efficiency improvement brought by parallel computing.

7. ```compare_two_models``` compares the evaluation results of two trained models and saves the better one.



#### Demo Description

1. ```prepare_data.ipynb``` demonstrates how to prepare the dataset. 
2. ```fasttext_pipeline.ipynb``` contains two sub pipelines with different parameters to train the fastTest model. The better one of two trained models will be saved.
3. ```fasttext_realtime_inference.ipynb``` first shows how to get the trained model from a completed experiment. Then, it demonstrates how to deploy the model with [Azure Container Instances](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-azure-container-instance), [Azure Machine Learning compute instance web service](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-local-container-notebook-vm), and [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-azure-kubernetes-service). Finally, it shows how to consume the deployed service.
4. ```fasttext_batch_inference.ipynb```  first shows how to get the trained model from a completed experiment.  Then, it demonstrates how to use the trained model as the input of the pipeline for batch inference.
<!-- #endregion -->
