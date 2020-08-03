## A sample of basic modules

This folder contains a simple sample of basic python modules.

### Declaration

To declare a module, you need to use the decorator `@dsl.module()` to decorate the python function `basic_module`.
Then with the command `az ml module build`, the arguments and return annotations of the function are analyzed
to generate the module spec file `sample_module.yaml`, which could be used for registering a module in AzureML.
The meta information (name, version, names, etc...) of the module could be declared as the arguments of `dsl.module`. 


### Execution

To invoke your function, we just need to call `ModuleExecutor(basic_module).execute(sys.argv)`.
The class `ModuleExecutor` will parse the command line args according to the function annotations,
convert the command line arguments to the arguments of the function `basic_module` and call the function.
In this simple `sample_module`, we simply print the input path and the input string parameter,
and write the string parameter to `output.txt` in the output directory.
In this way, the registered module could be run in AzureML with either Designer or module SDK.
The input/output path are the input/output ports in AzureML which could be linked with other modules.
The parameters are provided to the module with Designer UX or module SDK parameters.
