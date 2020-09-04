import argparse
import glob
import os
import sys
import json
import tempfile

import papermill

extension = '.ipynb'


exps = ["subcription_id = '<your subscription ID>'",
        "SUBSCRIPTION_ID = '<your subscription ID>'",
        "WORKSPACE_NAME = '<your workspace name>'",
        "workspace_name = '<your workspace name>'",
        "RESOURCE_GROUP_NAME = '<your resource group>'",
        "resource_group_name = '<your resource group>'",
        "!az login -o none",
        "!az account set -s $SUBSCRIPTION_ID",
        "!az ml folder attach -w $WORKSPACE_NAME -g $RESOURCE_GROUP_NAME"
        ]
# ws = "ws = Workspace.get(subscription_id='4faaaf21-663f-4391-96fd-47197c630979', resource_group='DesignerTestRG', name='DesignerTest-WCUS')\n"
# workspace = "workspace = Workspace.get(subscription_id='4faaaf21-663f-4391-96fd-47197c630979', resource_group='DesignerTestRG', name='DesignerTest-WCUS')\n"


def run_notebook(notebook, output_folder):
    papermill.execute_notebook(
        input_path=notebook,
        output_path=output_folder + "\\" + os.path.basename(notebook)[:-6] + "_output" + extension,
        log_output=True,
        # engine_name="azureml_engine",
    )

def replace_kernel_to_notebook(notebook_data):
    """
    Set kernel to notebook to default kernelspec in default conda environment
    :param notebook_data: the notebook data to set kernel
    :type notebook_data: dict
    """
    notebook_data['metadata']['kernelspec'] = dict(
        display_name="python3",
        language="python",
        name="python3"
    )

def replace_workspace(notebook_data, path):
    cells = notebook_data["cells"]
    for cell in cells:
        if cell["cell_type"] == "code":
            codes = cell["source"]
            for i in range(len(codes)):
                for exp in exps:
                    if exp in codes[i]:
                        codes[i] = ''
                    if "ws = Workspace.from_config()" in codes[i]:
                        codes[i] = "ws = Workspace.from_config('{}')\n".format(path)
                    if "workspace = Workspace.from_config()" in codes[i]:
                        codes[i] = "workspace = Workspace.from_config('{}')\n".format(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook_folder_directory', type=str, help='Notebook folder directory', required=True)

    args, _ = parser.parse_known_args(sys.argv)

    folder = args.notebook_folder_directory
    glob_path = args.notebook_folder_directory + "\*.ipynb"

    output_folder = folder + "\\notebook_output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for notebook in glob.glob(glob_path):
        with open(notebook) as nbfile:
            notebook_data = json.load(nbfile)

        replace_kernel_to_notebook(notebook_data)
        replace_workspace(notebook_data, path=folder)

        input_notebook = tempfile.mkstemp(suffix='.ipynb')[1]
        with open(input_notebook, 'w') as f:
            json.dump(notebook_data, f, indent=4)

        # Run Notebook
        try:
            print("===========================Running {}===========================".format(os.path.basename(notebook)))
            run_notebook(input_notebook, output_folder)
        except Exception as e:
            print(e)
            raise
