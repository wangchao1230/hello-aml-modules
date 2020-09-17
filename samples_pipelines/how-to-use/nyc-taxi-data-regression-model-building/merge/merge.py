import argparse
import os
from azureml.studio.core.io.data_frame_directory import load_data_frame_from_directory, save_data_frame_to_directory

print("Merge Green and Yellow taxi data")

parser = argparse.ArgumentParser("merge")
parser.add_argument("--cleansed_green_data", type=str, help="cleansed green data")
parser.add_argument("--cleansed_yellow_data", type=str, help="cleansed yellow data")
parser.add_argument("--output_merge", type=str, help="green and yellow taxi data merged")

args = parser.parse_args()
green_df = load_data_frame_from_directory(args.cleansed_green_data).data
yellow_df = load_data_frame_from_directory(args.cleansed_yellow_data).data
print("Argument (output merge taxi data path): %s" % args.output_merge)

# Appending yellow data to green data
combined_df = green_df.append(yellow_df, ignore_index=True)
combined_df.reset_index(inplace=True, drop=True)

if not (args.output_merge is None):
    os.makedirs(args.output_merge, exist_ok=True)
    print("%s created" % args.output_merge)
    save_data_frame_to_directory(args.output_merge, combined_df)