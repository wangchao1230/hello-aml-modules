import argparse
import os
import pandas as pd
from azureml.studio.core.io.data_frame_directory import load_data_frame_from_directory, save_data_frame_to_directory

print("Replace undefined values to relavant values and rename columns to meaningful names")

parser = argparse.ArgumentParser("normalize")
parser.add_argument("--filtered_data", type=str, help="filtered taxi data")
parser.add_argument("--output_normalize", type=str, help="replaced undefined values and renamed columns")

args = parser.parse_args()
combined_converted_df = load_data_frame_from_directory(args.filtered_data).data
print("Argument (output normalized taxi data path): %s" % args.output_normalize)

# These functions replace undefined values and rename to use meaningful names.
replaced_stfor_vals_df = (combined_converted_df.replace({"store_forward": "0"}, {"store_forward": "N"})
                          .fillna({"store_forward": "N"}))

replaced_distance_vals_df = (replaced_stfor_vals_df.replace({"distance": ".00"}, {"distance": 0})
                             .fillna({"distance": 0}))

normalized_df = replaced_distance_vals_df.astype({"distance": 'float64'})

temp = pd.DatetimeIndex(normalized_df["pickup_datetime"])
normalized_df["pickup_date"] = temp.date
normalized_df["pickup_time"] = temp.time

temp = pd.DatetimeIndex(normalized_df["dropoff_datetime"])
normalized_df["dropoff_date"] = temp.date
normalized_df["dropoff_time"] = temp.time

del normalized_df["pickup_datetime"]
del normalized_df["dropoff_datetime"]

normalized_df.reset_index(inplace=True, drop=True)

if not (args.output_normalize is None):
    os.makedirs(args.output_normalize, exist_ok=True)
    print("%s created" % args.output_normalize)
    save_data_frame_to_directory(args.output_normalize, normalized_df)