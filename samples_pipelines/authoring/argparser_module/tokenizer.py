# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import codecs


def run_tokenizer(args):
    print(args)


def main():
    # Parsing arguments
    parser = argparse.ArgumentParser("Tokenizer", description="This is a example tokenizer.")
    parser.add_argument("-i", "--input_file_path", required=True, type=str, help="Input text file path")
    parser.add_argument("-o", "--output_dir_path", required=True, type=str, help="Output file directory path")
    parser.add_argument("--output_to_file", type=int, default=0, help="whether to interpret output_dir_path as file to write to, or folder containing file to write to")
    parser.add_argument("--input_is_tsv", type=int, default=0, help="bool determining whether to use tsv related options")
    parser.add_argument("--delimiter", type=str, default=None, help="optional, delimiter to use if parsing a tsv type file")
    parser.add_argument("--ignore_cols", type=int, nargs='+', help='indices of columns to ignore if parsing a tsv', default=[])
    parser.add_argument("-m", "--mode", choices=["train", "inference", "spacy"], default="train", help="Tokenizer to use [train, inference, spacy]")
    parser.add_argument("-t", "--type", choices=["word", "sentence"], default="word", help="Whether to use word tokenizer or sentence tokenizer")
    args = parser.parse_args()

    if not args.input_file_path or not args.output_dir_path:
        parser.print_usage()
        return(1)

    if args.input_is_tsv:
        args.delimiter = codecs.decode(args.delimiter, 'unicode_escape')
    args.ignore_cols = set(args.ignore_cols) # faster lookup
    run_tokenizer(args)


if __name__ == '__main__':
    main()
