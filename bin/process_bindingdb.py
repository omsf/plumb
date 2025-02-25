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
    parser.add_argument('--input-dir', type=Path, required = True, help='SDF file to process')
    return parser.parse_args()


def process_sdf_files(input_dir):
    """
    Process SDF files in the specified directory, checking for 3D coordinates
    and extracting ligand metadata.

    Args:
        input_dir (Path): Directory containing SDF files.

    Returns:
        pd.DataFrame: Processed ligand information.
    """
    # Find all SDF files that include '3D' in their filename
    sdfs = list(input_dir.glob('*3D.sdf'))

    output = []

    for sdf in tqdm(sdfs[:10], desc="Processing SDF Files"):
        # Load individual ligands from the SDF file (ASAP function)
        mols: list[Ligand] = MolFileFactory(filename=sdf).load()

        for mol in mols:
            # Extract relevant ligand information
            mol_dict = {
                'compound_name': mol.compound_name,
                'filename': sdf.name,
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
                mol.to_sdf(f'{mol.compound_name}.sdf')

            output.append(mol_dict)

    # Convert extracted data to a pandas DataFrame
    return pd.DataFrame.from_records(output)

def save_results(df):
    """
    Save the processed ligand information to CSV and JSON files.

    Args:
        df (pd.DataFrame): DataFrame containing processed ligand data.
    """
    df.to_csv('processed_bindingdb.csv', index=False)

    # Separate and save 2D and 3D ligand information
    df_2d = df[~df['has_3d']]  # Fixed: Corrected filtering for 2D molecules
    # df_2d = df[df['has_3d']]
    df_3d = df[df['has_3d']]

    df_2d.to_csv('2d_bindingdb.csv', index=False)
    df_3d.to_csv('3d_bindingdb.csv', index=False)

    # Save unique 3D SDF filenames
    unique_sdf_filenames = df_3d['filename'].unique()
    with open('unique_3D_sdf_filenames.txt', 'w') as f:
        for filename in unique_sdf_filenames:
            f.write(f'{filename}\n')

    # Write each ligand's data to a separate JSON file
    for record in df_3d.to_dict(orient='records'):
        with open(f'{record["compound_name"]}.json', 'w') as f:
            json.dump(record, f, indent=4)


def main():
    # args = parse_args()
    """Main function to parse arguments, process SDF files, and save results."""
    args = parse_args()
    df = process_sdf_files(args.input_dir)
    save_results(df)

if __name__ == '__main__':
    main()
