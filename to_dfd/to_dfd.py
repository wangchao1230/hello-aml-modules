import argparse
from azureml.studio.core.io.data_frame_directory import DataFrameDirectory
import pandas as pd

parser = argparse.ArgumentParser(description="Convert TSV/CSV file into the data frame directory format of AML.")
parser.add_argument('input', metavar='Input file path', type=str, help='The path of input TSV/CSV file')
parser.add_argument('output', metavar='Output folder path', type=str, help='The output folder path of data frame directory')
#parser.add_argument('-d', '--delimeter', help='Delimeter,  is default value', type=str, default='comma')   

args = parser.parse_args()
print("Converting %s to dataframe directory in %s" % (args.input, args.output))
#print("Delimeter=%s" % args.delimeter)

df = pd.read_csv(args.input, sep=None, quoting=3, engine='python')
dfd = DataFrameDirectory.create(df, compute_stats_in_visualization=True)
dfd.dump(args.output)

print('Done.')