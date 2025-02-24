"""
Author: Alex Payne
Adapted by: Ariana Brenner Clerkin
This script enables reading in a csv and writing out each row of the csv as a json file.
This enables the next step of the pipeline to have a single channel input that can be controlled easily.
"""

import argparse
import pandas as pd
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_dir", type=Path, help="Path to the input structure directory."
    )
    parser.add_argument(
        "input_parquet", type=Path, help="Path to the input parquet file."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data = pd.read_parquet(args.input_parquet, engine="pyarrow")
    data.fillna("", inplace=True)
    data.to_csv("info.csv")
    
    ## TO DO FIX JSON CONVERSION

    # rename_dict = {
    #     "system_id": "unique_id",
    # }
    # changed = data.rename(columns=rename_dict)
    # for record in changed.to_dict(orient="records"):
    #     new_record = NewRecord(
    #         **record,
    #         home=str(args.input_dir / record["unique_id"]),
    #         rcsb_id=record["unique_id"][0:4]
    #     )
    #     new_record.write_json_file(write_to_home=False)

if __name__ == "__main__":
    main()