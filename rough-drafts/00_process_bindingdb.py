"""
Assess which SDF files actually have 3D coordinates
"""
from asapdiscovery.data.schema.ligand import Ligand
from asapdiscovery.data.readers.molfile import MolFileFactory
from argparse import ArgumentParser
import pandas as pd
from pathlib import Path
from tqdm import tqdm

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--input-dir', type=Path, help='SDF file to process')
    return parser.parse_args()


def main():
    args = parse_args()

    # get all sdf files
    sdfs = list(args.input_dir.glob('*3D.sdf'))

    output = []
    for sdf in tqdm(sdfs):

        # asap function to read separate ligands from a multi-ligand sdf file
        mols: list[Ligand] = MolFileFactory(filename=sdf).load()

        # create a dictionary for each ligand containing various relevant information
        # there are some hidden choices here, for instance OpenEye is adding hydrogens which you might not want
        for mol in mols:
            mol_dict = {'compound_name': mol.compound_name,
                        'filename': sdf.name,
                        'has_3d': mol.to_oemol().GetDimension() == 3,
                        'num_atoms': mol.to_oemol().NumAtoms(),
                        'smiles': mol.smiles,
                        }

            # any data in the SDF file is saved to the 'tags' attribute of an asapdiscovery Ligand object
            mol_dict.update(mol.tags)
            output.append(mol_dict)

    df = pd.DataFrame.from_records(output)
    df.to_csv('processed_bindingdb.csv', index=False)

    # write separate csvs for 2D and 3D
    df_2d = df[df['has_3d']]
    df_3d = df[df['has_3d']]
    df_2d.to_csv('2d_bindingdb.csv', index=False)
    df_3d.to_csv('3d_bindingdb.csv', index=False)

    # get unique sdf filenames with 3D coordinates
    unique_sdf_filenames = df_3d['filename'].unique()
    with open('unique_3D_sdf_filenames.txt', 'w') as f:
        for filename in unique_sdf_filenames:
            f.write(f'{filename}\n')


if __name__ == '__main__':
    main()
