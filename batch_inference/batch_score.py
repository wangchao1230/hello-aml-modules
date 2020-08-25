# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import os
import sys
import numpy as np
import tensorflow as tf
from PIL import Image
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl


@dsl.module(
    name="Batch Score",
    version='0.0.1',
    description='digit identification',
    job_type='parallel',
    conda_dependencies='conda.yaml',
    parallel_inputs=[InputDirectory(name='Images to score')],
    base_image='mcr.microsoft.com/azureml/intelmpi2018.3-cuda10.0-cudnn7-ubuntu16.04'
)
def batch_score(
    scored_data_output_dir: OutputDirectory(),
    model_dir: InputDirectory(),
    scored_data_output_name: str
):
    global g_tf_sess
    global output_file

    print('=====================================================')
    print(f'scored_data_output_dir: {scored_data_output_dir}')
    # contruct graph to execute
    tf.reset_default_graph()
    saver = tf.train.import_meta_graph(os.path.join(model_dir, 'mnist-tf.model.meta'))
    g_tf_sess = tf.Session(config=tf.ConfigProto(device_count={'GPU': 0}))
    saver.restore(g_tf_sess, os.path.join(model_dir, 'mnist-tf.model'))
    output_file = os.path.join(scored_data_output_dir, f"{scored_data_output_name}")

    def run(mini_batch):
        print(f'run method start: {__file__}, run({mini_batch})')
        resultList = []
        in_tensor = g_tf_sess.graph.get_tensor_by_name("network/X:0")
        output = g_tf_sess.graph.get_tensor_by_name("network/output/MatMul:0")

        for image in mini_batch:
            # prepare each image
            data = Image.open(image)
            np_im = np.array(data).reshape((1, 784))
            # perform inference
            inference_result = output.eval(feed_dict={in_tensor: np_im}, session=g_tf_sess)
            # find best probability, and add to result list
            best_result = np.argmax(inference_result)
            result_line = "{}: {}\n".format(os.path.basename(image), best_result)
            print(result_line)
            f = open(output_file, 'a')
            f.write(result_line)
            f.close()
            resultList.append(result_line)

        return resultList

    return run


# This main code is only used for local debugging, will never be reached in AzureML when it is a parallel module.
# See https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-run-step#write-your-inference-script
if __name__ == '__main__':
    ModuleExecutor(batch_score).execute(sys.argv)
