# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
import runpy
from enum import Enum
from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, EnumParameter, StringParameter, IntParameter, InputDirectory, OutputDirectory


class EnumMode(Enum):
    train = 'train'
    inference = 'inference'
    spacy = 'spacy'


class EnumType(Enum):
    word = 'word'
    sentence = 'sentence'


@dsl.module(
    name='Tokenizer',
    description='This is a example tokenizer.',
)
def tokenizer(
    input_file_path: InputDirectory(description="Input text file path"),
    output_dir_path: OutputDirectory(description="Output file directory path"),
    output_to_file: IntParameter(description="whether to interpret output_dir_path as file to write to, or folder containing file to write to") = 0,
    input_is_tsv: IntParameter(description="bool determining whether to use tsv related options") = 0,
    delimiter: StringParameter(description="optional, delimiter to use if parsing a tsv type file") = None,
    ignore_cols: IntParameter(description="indices of columns to ignore if parsing a tsv") = None,
    mode: EnumParameter(enum=EnumMode, description="Tokenizer to use [train, inference, spacy]") = EnumMode.train,
    type: EnumParameter(enum=EnumType, description="Whether to use word tokenizer or sentence tokenizer") = EnumType.word,
):
    sys.argv = [
        'tokenizer.py',
        '-i', str(input_file_path),
        '-o', str(output_dir_path),
        '--output_to_file', str(output_to_file),
        '--input_is_tsv', str(input_is_tsv),
        '-m', mode.value,
        '-t', type.value,
    ]
    if delimiter is not None:
        sys.argv += ['--delimiter', str(delimiter)]
    if ignore_cols is not None:
        sys.argv += ['--ignore_cols', str(ignore_cols)]
    print(' '.join(sys.argv))
    runpy.run_path('tokenizer.py', run_name='__main__')


if __name__ == '__main__':
    ModuleExecutor(tokenizer).execute(sys.argv)
