# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
import torch
import pandas as pd
from uuid import uuid4
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from PIL import Image
from torchvision import transforms
from torchvision.datasets import MNIST
import torch.nn as nn
import os
from pathlib import Path

from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import InputDirectory, OutputDirectory, ModuleExecutor


transform = transforms.Compose([
               transforms.ToTensor(),
               transforms.Normalize((0.1307,), (0.3081,))
            ])


@dsl.module(
    name='Parallel Score Images',
    version='0.0.1',
    job_type='parallel',
    parallel_inputs=[
        InputDirectory(name='Images to score'),
        InputDirectory(name='Optional images to score', optional=True)
    ],
)
def parallel_score_images(
    scored_dataset: OutputDirectory(),
    trained_model: InputDirectory() = None,
):
    # Use the path of a prepared model if trained_model is None
    if trained_model is None:
        trained_model = str(Path(__file__).parent / 'tests/parallel_score_images/inputs/trained_model/')
    print("Scored dataset:", scored_dataset)
    print("Trained model:", trained_model)
    map_location = 'cpu' if not torch.cuda.is_available() else None
    model = torch.load(os.path.join(trained_model, 'model.pt'), map_location=map_location)
    os.makedirs(scored_dataset, exist_ok=True)
    print("Model is loaded:", model)

    def run(files):
        if len(files) == 0:
            return []
        results = []
        nthreads = min(2*cpu_count(), len(files))

        print(f"Ready to process {len(files)} images.")
        print('\n'.join(files))
        with ThreadPool(nthreads) as pool:
            imgs = pool.map(Image.open, files)

        for f, img in zip(files, imgs):
            img = Image.open(f)
            tensor = transform(img).unsqueeze(0)
            if torch.cuda.is_available():
                tensor = tensor.cuda()

            with torch.no_grad():
                output = model(tensor)
                softmax = nn.Softmax(dim=1)
                pred_probs = softmax(output).cpu().numpy()[0]
                index = torch.argmax(output, 1)[0].cpu().item()
                result = {'Filename': Path(f).name, 'Class': MNIST.classes[index]}
                for c, prob in zip(MNIST.classes, pred_probs):
                    result[f"Prob of {c}"] = prob
            results.append(result)
        columns = sorted(list(results[0].keys()))
        df = pd.DataFrame(results, columns=columns)
        print("Result:")
        print(df)
        output_file = os.path.join(scored_dataset, f"{uuid4().hex}.parquet")
        df.to_parquet(output_file, index=False)
        return results
    return run


# This main code is only used for local debugging, will never be reached in AzureML when it is a parallel module.
# See https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-run-step#write-your-inference-script
if __name__ == '__main__':
    ModuleExecutor(parallel_score_images).execute(sys.argv)
