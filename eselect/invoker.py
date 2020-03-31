import re
import shlex
import subprocess
import sys


def run(command: str, timeout=60000):
    if not command:
        return

    return subprocess.Popen(shlex.split(command), stdout=sys.stdout, stderr=sys.stderr).wait(timeout=timeout)


INVOKER_VERSION = '0.0.5'
COMMAND_OPTION_PATTERN = re.compile(r"^--(\w|-)+=([\n]|.)+", re.MULTILINE)


def is_invoking_official_module(args):
    return len(args) >= 3 and args[0] == 'python' and args[1] == '-m' and args[2].startswith('azureml.studio.')


def quote(arg):
    # If it matches the --<key>=<value> pattern, and the value isn't empty
    # Take the shlex.quote action to the value part only
    if re.search(COMMAND_OPTION_PATTERN, arg):
        # Split by the first '='
        parts = arg.split("=", 1)
        return '{}={}'.format(parts[0], shlex.quote(parts[1]))
    return shlex.quote(arg)


def generate_run_command(args):
    return ' '.join(quote(arg) for arg in args)


def execute(args):
    is_custom_module = not is_invoking_official_module(args)
    module_type = 'custom module' if is_custom_module else 'official module'
    print('Invoking {} by invoker {}.'.format(module_type, INVOKER_VERSION))

    ret = run(generate_run_command(args))

    # set the subprocess run result as exit value
    exit(ret)


if __name__ == '__main__':
    args = sys.argv[1:]
    execute(args)
