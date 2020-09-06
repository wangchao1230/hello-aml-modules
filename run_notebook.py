import argparse
import glob
import os
import sys
import json
import tempfile
import ast
import astunparse

import papermill

extension = '.ipynb'

exps = ["your subscription ID",
        "your workspace name",
        "your resource group",
        "!az login -o none",
        "!az account set -s $SUBSCRIPTION_ID",
        "!az ml folder attach -w $WORKSPACE_NAME -g $RESOURCE_GROUP_NAME"
        ]

ws_get = ast.parse("ws = Workspace.get(subscription_id='4faaaf21-663f-4391-96fd-47197c630979', resource_group='DesignerTestRG', name='DesignerTest-WCUS')\n").body[0]
workspace_get = ast.parse("workspace = Workspace.get(subscription_id='4faaaf21-663f-4391-96fd-47197c630979', resource_group='DesignerTestRG', name='DesignerTest-WCUS')\n").body[0]

ws_config = ast.parse("ws = Workspace.from_config()\n").body[0]
workspace_config = ast.parse("workspace = Workspace.from_config()\n").body[0]


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


def parse_ast(code_cell):
    """
    Parse the code ast obj from cell source code.

    :param code_cell: the code cell to be parsed.
    :type: dict

    :return: The ast.
    :rtype: ast obj
    """
    source = ''.join([line for line in code_cell['source']])
    if "!az" not in source:
        try:
            cell_ast = ast.parse(source)
        except Exception as e:
            print("Error occurs while trying to ast parse code in notebook")
            print(e)
            raise
        return cell_ast
    return None


def replace_workspace(notebook_data):
    cells = notebook_data.get('cells')

    for cell_itr in range(len(cells)):
        cell = cells[cell_itr]
        if cell.get('cell_type') != 'code':
            continue

        codes = cell["source"]
        for i in range(len(codes)):
            for exp in exps:
                if exp in codes[i]:
                    codes[i] = ''

        cell_ast = parse_ast(cell)

        if cell_ast is None:
            continue

        for itr in range(len(cell_ast.body)):
            ast_obj = cell_ast.body[itr]
            if isinstance(ast_obj, ast.Assign) and \
                    isinstance(ast_obj.value, ast.Call) and \
                    isinstance(ast_obj.value.func, ast.Attribute) and \
                    isinstance(ast_obj.value.func.value, ast.Name) and \
                    ast_obj.value.func.value.id == 'Workspace':
                if ast_obj.value.func.attr == 'get':
                    if ast_obj.targets[0].id == 'ws':
                        cell_ast.body[itr].body = [ws_get]
                    elif ast_obj.targets[0].id == 'workspace':
                        cell_ast.body[itr].body = [workspace_get]
                elif ast_obj.value.func.attr == 'from_config':
                    if ast_obj.targets[0].id == 'ws':
                        cell_ast.body[itr].body = [ws_config]
                    elif ast_obj.targets[0].id == 'workspace':
                        cell_ast.body[itr].body = [workspace_config]
                notebook_data['cells'][cell_itr]['source'] = astunparse.unparse(cell_ast)


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
        replace_workspace(notebook_data)

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
