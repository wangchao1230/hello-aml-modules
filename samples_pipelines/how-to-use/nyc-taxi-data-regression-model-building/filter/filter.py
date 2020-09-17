import argparse
import os
from azureml.studio.core.io.data_frame_directory import load_data_frame_from_directory, save_data_frame_to_directory

print("Filters out coordinates for locations that are outside the city border.",
      "Chain the column filter commands within the filter() function",
      "and define the minimum and maximum bounds for each field.")


parser = argparse.ArgumentParser("filter")
parser.add_argument("--merged_data", type=str, help="merged taxi data")
parser.add_argument("--output_filter", type=str, help="filter out out of city locations")

args = parser.parse_args()

combined_df = load_data_frame_from_directory(args.merged_data).data

print("Argument (output filtered taxi data path): %s" % args.output_filter)

# These functions filter out coordinates for locations that are outside the city border.

# Filter out coordinates for locations that are outside the city border.
# Chain the column filter commands within the filter() function
# and define the minimum and maximum bounds for each field

combined_df = combined_df.astype({"pickup_longitude": 'float64', "pickup_latitude": 'float64',
                                  "dropoff_longitude": 'float64', "dropoff_latitude": 'float64'})

latlong_filtered_df = combined_df[(combined_df.pickup_longitude <= -73.72) &
                                  (combined_df.pickup_longitude >= -74.09) &
                                  (combined_df.pickup_latitude <= 40.88) &
                                  (combined_df.pickup_latitude >= 40.53) &
                                  (combined_df.dropoff_longitude <= -73.72) &
                                  (combined_df.dropoff_longitude >= -74.72) &
                                  (combined_df.dropoff_latitude <= 40.88) &
                                  (combined_df.dropoff_latitude >= 40.53)]

latlong_filtered_df.reset_index(inplace=True, drop=True)

if not (args.output_filter is None):
    os.makedirs(args.output_filter, exist_ok=True)
    print("%s created" % args.output_filter)
    save_data_frame_to_directory(args.output_filter, latlong_filtered_df)