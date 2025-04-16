"""
Assess which SDF files actually have 3D coordinates
"""

### Import modules
import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from asapdiscovery.data.schema.ligand import Ligand
from asapdiscovery.data.readers.molfile import MolFileFactory


def parse_args():
    """
    Parse command-line arguments.
    
    Returns: 
        argparse.Namespace: Parsed arguments containing the input directory
    """
    parser = ArgumentParser()
    parser.add_argument('--input-file', type=Path, required = True, help='Path to single SDF file')
    return parser.parse_args()


def process_sdf_files(sdf_file):
    """
    Process a single SDF file to extract ligand information and check for 3D coordinates.

    Args:
        sdf_file (Path): Path to the SDF file.

    Returns:
        pd.DataFrame: Dataframe containing ligand information.
    """
    output = []
    mols: list[Ligand] = MolFileFactory(filename=sdf_file).load()

    for mol in mols:
        # Extract relevant ligand information
        mol_dict = {
                'compound_name': mol.compound_name,
                'filename': sdf_file.name,
                'has_3d': mol.to_oemol().GetDimension() == 3,
                'num_atoms': mol.to_oemol().NumAtoms(),
                'smiles': mol.smiles,
                'pdb_id': mol.tags.get('PDB ID', '')[:4] if mol.tags.get('PDB ID') else '',
        }

        # Include additional metadata from the SDF file
        # mol.tags is from the Ligand object. 
        mol_dict.update(mol.tags)

        # Save SDF file for molecules confirmed to have 3D coordinates
         # This breaks out head ligand into its own sdf
        if mol_dict['has_3d']:
            output_sdf = f'{mol.compound_name}.sdf'
            print(f"Writing SDF file: {output_sdf}")  # Debugging
            mol.to_sdf(f'{mol.compound_name}.sdf')

        output.append(mol_dict)

    # Convert extracted data to a pandas DataFrame
    return pd.DataFrame.from_records(output)

def save_results(df, input_file):
    """
    Save the processed ligand information to CSV and JSON files.

    Args:
        df (pd.DataFrame): DataFrame containing processed ligand data.
        input_file (Path): Original input file for naming outputs.
    """
    base_name = input_file.stem
    df.to_csv(f'{base_name}_processed.csv', index=False)

    # Separate and save 2D and 3D ligand information
    df_2d = df[~df['has_3d']]  # Fixed: Corrected filtering for 2D molecules
    # df_2d = df[df['has_3d']]
    df_3d = df[df['has_3d']]

    df_2d.to_csv(f'{base_name}_2d.csv', index=False)
    df_3d.to_csv(f'{base_name}_3d.csv', index=False)

    # Save unique 3D SDF filenames
    with open(f'{base_name}_3d.json', 'w') as f:
        json.dump(df_3d.to_dict(orient='records'), f, indent=4)

    # # Write each ligand's data to a separate JSON file
    # for record in df_3d.to_dict(orient='records'):
    #     with open(f'{record["compound_name"]}.json', 'w') as f:
    #         json.dump(record, f, indent=4)


def main():
    # args = parse_args()
    """Main function to parse arguments, process SDF files, and save results."""
    args = parse_args()
    df = process_sdf_files(args.input_file)
    save_results(df, args.input_file)

if __name__ == '__main__':
    main()
