import argparse
import glob
import os
import sys
import json
import tempfile

import papermill

extension = '.ipynb'

exps = ["!az login -o none",
        "!az account set -s $SUBSCRIPTION_ID",
        "!az ml folder attach -w $WORKSPACE_NAME -g $RESOURCE_GROUP_NAME"]


def run_notebook(notebook, output_folder):
    papermill.execute_notebook(
        input_path=notebook,
        output_path=output_folder + "\\" + os.path.basename(notebook)[:-6] + "_output" + extension,
        log_output=True,
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


def remove_exps(notebook_data):
    cells = notebook_data.get('cells')

    for cell_itr in range(len(cells)):
        cell = cells[cell_itr]
        if cell.get('cell_type') != 'code':
            continue

        codes = cell["source"]
        for i in range(len(codes)):
            for exp in exps:
                if exp in codes[i]:
                    cell["source"][i] = ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook_folder_directory', type=str, nargs='+', help='Notebook folder directory', required=True)

    args, _ = parser.parse_known_args(sys.argv)

    folder_list = args.notebook_folder_directory

    for folder in folder_list:
        print('START: Running Notebooks in {}.'.format(folder))
        glob_path = folder + "\*.ipynb"

        output_folder = folder + "\\notebook_output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for notebook in glob.glob(glob_path):
            with open(notebook) as nbfile:
                notebook_data = json.load(nbfile)

            replace_kernel_to_notebook(notebook_data)
            remove_exps(notebook_data)

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
