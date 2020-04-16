from os import walk
import argparse
from os import listdir
from os.path import isfile, join

parser = argparse.ArgumentParser("walk")
parser.add_argument("--path", type=str, help="Path of file/folder")

args = parser.parse_args()

p = args.path

if (isfile(p)):
    print(p)
else:
    onlyfiles = [f for f in listdir(p) if isfile(join(p, f))]
    for f in onlyfiles:
        print(f)