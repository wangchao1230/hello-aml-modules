from __future__ import print_function

import horovod.torch as hvd

hvd.init()
print("Mpi rank: ", hvd.rank(), " size: ", hvd.size(), " local rank: ", hvd.local_rank())