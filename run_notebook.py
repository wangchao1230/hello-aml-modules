import argparse
import glob
import os
import sys
import json
import tempfile
import time

import papermill

extension = '.ipynb'

exps = ["!az login -o none",
        "!az account set -s $SUBSCRIPTION_ID",
        "!az ml folder attach -w $WORKSPACE_NAME -g $RESOURCE_GROUP_NAME"]


def run_notebook(notebook, output_folder, notebook_file_name):
    papermill.execute_notebook(
        input_path=notebook,
        output_path=output_folder + "\\" + notebook_file_name[:-6] + "_output" + extension,
        log_output=True,
    )


def replace_kernel_to_notebook(notebook_data):
    """
    Set kernel to notebook to default kernelspec in default conda environment
    :param notebook_data: the notebook data to set kernel
    :type notebook_data: dict
    """
    if 'metadata' in notebook_data.keys():
        if 'kernelspec' in notebook_data['metadata'].keys():
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
                    notebook_data['cells'][cell_itr]["source"][i] = ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook_folder_directory', type=str, nargs='+', help='Notebook folder directory', required=True)
    parser.add_argument('--notebooks_to_skip', type=str, nargs='+', help='Skipped notebooks')
    parser.add_argument('--fail_fast_flag', type=bool, help='Whether to stop running notebooks immediately when error occurs')

    args, _ = parser.parse_known_args(sys.argv)

    folder_list = args.notebook_folder_directory
    notebooks_to_skip = args.notebooks_to_skip
    if notebooks_to_skip is None:
        print("notebooks_to_skip:", notebooks_to_skip)
        notebooks_to_skip = []
    fail_fast_flag = args.fail_fast_flag

    summary = "\n\n=============================RUN SUMMARY=============================\n"

    succeed_flag = True
    for folder_path in folder_list:
        # go back to run_notebook.py root path
        os.chdir(sys.path[0])
        # enter notebooks path
        os.chdir(folder_path)
        folder = "../" + os.path.basename(folder_path)

        failed_notebooks = 0
        summary += "Notebooks in {} \n".format(folder)
        print('START: Running Notebooks in {}.'.format(folder))
        glob_path = folder + "\*.ipynb"

        output_folder = folder + "\\notebook_output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        notebooks = glob.glob(glob_path)
        for notebook in notebooks:
            notebook_file_name = os.path.basename(notebook)
            # Skip this notebook
            if notebook_file_name in notebooks_to_skip:
                continue

            with open(notebook) as nbfile:
                notebook_data = json.load(nbfile)

            replace_kernel_to_notebook(notebook_data)
            remove_exps(notebook_data)

            input_notebook = tempfile.mkstemp(suffix='.ipynb')[1]
            with open(input_notebook, 'w') as f:
                json.dump(notebook_data, f, indent=4)

            # Run Notebook
            try:
                print("\n==============Running {}==============".format(notebook_file_name))
                start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                start_time2 = time.time()
                run_notebook(input_notebook, output_folder, notebook_file_name)
                end_time2 = time.time()
                end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                summary += "[Success] Run notebook {0} elapsed: {1} seconds. Start time: {2}, End Time: {3}.\n".format(notebook_file_name, round(end_time2-start_time2, 2), start_time, end_time)
            except Exception as e:
                print(e)
                succeed_flag = False
                failed_notebooks += 1
                summary += "[Failed] Run notebook {0} Failed!!! Start time: {1}.\n".format(notebook_file_name, start_time)
                if fail_fast_flag:
                    print(summary)
                    raise

        summary += "Success notebooks {0}/total {1}.\n\n".format(len(notebooks)-failed_notebooks, len(notebooks))

    print(summary)
    if succeed_flag is False:
        raise Exception("Run Failed, please refer to Summary above for more information.")
