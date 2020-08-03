# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
from pathlib import Path

from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory


@dsl.module(
    name="MPI Module",
    job_type='mpi'
)
def mpi_module(
        output_dir: OutputDirectory(),
        input_dir: InputDirectory() = '.',
        param0: str = 'abc',
        param1: int = 10,
):
    from mpi4py import MPI
    for k, v in locals().items():
        print(f"{k}: {v}")
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    print(f"This is an MPI module, I'm rank {rank}/{size}.")
    if rank == 0:
        print("I will write data.")
        output_dir = Path(output_dir)
        with open(output_dir / f"output.txt", 'w') as fout:
            fout.write(param0)
            fout.write(str(param1))
    else:
        print("I don't return data.")


if __name__ == '__main__':
    ModuleExecutor(mpi_module).execute(sys.argv)
