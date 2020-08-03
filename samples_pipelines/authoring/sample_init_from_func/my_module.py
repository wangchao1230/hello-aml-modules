# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from pathlib import Path


class MyEnum(Enum):
    enum0 = 0
    enum1 = 1


def add(
    output_file: Path,
    a=1,
    b=2,
    c=3,
):
    output_file = Path(output_file)
    with open(output_file, 'w') as fout:
        fout.write(str(a + b + c))
