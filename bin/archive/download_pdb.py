"""
Download PDB files from the PDB database.
"""
import argparse
from pathlib import Path
from asapdiscovery.data.services.rcsb.rcsb_download import download_pdb_structure
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=Path, help="Path to the input csv file.")
    return parser.parse_args()


def main():
    args = parse_args()

    # Check if the input file exists
    if not args.input_json.exists():
        raise FileNotFoundError(f"Input file {args.input_json} does not exist.")

    # Load JSON file
    with open(args.input_json, "r") as f:
        record_dict = json.load(f)

    # Validate JSON structure
    if 'pdb_id' not in record_dict:
        raise KeyError("Missing 'pdb_id' in input JSON.")
    
    pdb_id = record_dict['pdb_id']
    print(f"Downloading PDB file for ID: {pdb_id}")

    try:
        downloaded = download_pdb_structure(pdb_id, "./", file_format="cif")
        if not downloaded:
            raise ValueError("Download failed, received empty response.")
        print(f"Downloaded file path: {downloaded}")
    except Exception as e:
        print(f"Error downloading PDB file: {e}")
        return

    record_dict['cif'] = downloaded
    with open(args.input_json, "w") as f:
        json.dump(record_dict, f)


if __name__ == '__main__':
    main()