## A sample of basic modules with more annotation types

This folder contains a sample of basic python module with different annotation types.

### Declaration

This module declares 4 types of inputs/outputs: `InputFile`, `InputDirectory`, `OutputFile`, `OutputDirectory`
and 5 different parameter types:
string, integer, float, bool, enum.
The 5 parameter types correspond to 5 valid types in the module spec definition.
As for input/output ports, AzureML allows a user define any port types.
With the annotation `OutputDirectory(type='MyDirectory')`,
the user defined a directory output port with the port type `MyDirectory`.
 
### Execution

When invoking the function, we call `ModuleExecutor(sample_module).execute(sys.argv)`.
The command line will be parsed according to the types of annotations then pass to the function.
For the 5 parameter types, the command line value will parsed as the corresponding python types.
As for `InputFile`, `InputDirectory`, `OutputFile`, `OutputDirectory`,
the path string will be passed to the function, the user code could use `os.path` or `pathlib.Path` to handle them.
If the type is `OutputDirectory`, the directory will be created before calling the user function.
