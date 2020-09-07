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
                    notebook_data['cells'][cell_itr]["source"][i] = ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook_folder_directory', type=str, nargs='+', help='Notebook folder directory', required=True)
    parser.add_argument('--fail_fast_flag', type=bool, help='Whether to stop running notebooks immediately when error occurs')

    args, _ = parser.parse_known_args(sys.argv)

    folder_list = args.notebook_folder_directory
    fail_fast_flag = args.fail_fast_flag

    summary = "\n\n=============================RUN SUMMARY=============================\n"

    succeed_flag = True
    for folder in folder_list:
        failed_notebooks = 0
        summary += "Notebooks in {} \n".format(folder)
        print('START: Running Notebooks in {}.'.format(folder))
        glob_path = folder + "\*.ipynb"

        output_folder = folder + "\\notebook_output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        notebooks = glob.glob(glob_path)
        for notebook in notebooks:
            with open(notebook) as nbfile:
                notebook_data = json.load(nbfile)

            replace_kernel_to_notebook(notebook_data)
            remove_exps(notebook_data)

            input_notebook = tempfile.mkstemp(suffix='.ipynb')[1]
            with open(input_notebook, 'w') as f:
                json.dump(notebook_data, f, indent=4)

            # Run Notebook
            try:
                notebook_file_name = os.path.basename(notebook)
                print("==============Running {}==============".format(notebook_file_name))
                start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                start_time2 = time.time()
                run_notebook(input_notebook, output_folder)
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
