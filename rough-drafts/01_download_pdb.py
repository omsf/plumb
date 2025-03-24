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
    with open(args.input_json, "r") as f:
        record_dict = json.load(f)
    downloaded = download_pdb_structure(record_dict['pdb_id'], "./", file_format="cif1")
    record_dict['cif'] = downloaded
    with open(args.input_json, "w") as f:
        json.dump(record_dict, f)


if __name__ == '__main__':
    main()
