# A sample of module with external dependencies

In some scenarios users might be developing dls.modules with external dependencies.

Source directory is brought to deal with such cases.

All resources(spec, test, notebook, vscode configs) will be generated under source directory. 

That way, user can make sure module can find right external dependencies by changing source directory.

In this case, module `module1/module1.py` referenced `package1/foo.py`. 
So source directory is set to folder `complex_module` to make sure `module1/module1.py` can find `package1/foo.py` correctly.