## A sample of MPI modules

This folder contains an MPI module which could run on multiple nodes in AzureML.
The nodes could communicate with each other using [MPI](https://en.wikipedia.org/wiki/Message_Passing_Interface).

### Declaration
To declare an MPI module, you just need to set `job_type='mpi'` when declaring `dsl.module`.
Thus the module spec generated by this module will be registered as an MPI module.

### Execution
The function `mpi_module` in `mpi_module.py` has one input directory and two input parameters.
It uses [mpi4py](https://pypi.org/project/mpi4py/) to get the information of MPI environment.
Since all nodes' bind to the same path in AzureBlobStorage, only the node with rank 0 will write the output data.
The other nodes do not return anything.
 