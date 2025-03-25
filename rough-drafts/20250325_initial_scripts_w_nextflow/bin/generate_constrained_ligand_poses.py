"""
Generate constrained ligand poses using OpenEye tooling
"""
from asapdiscovery.data.schema.complex import PreppedComplex
from asapdiscovery.data.readers.molfile import MolFileFactory
from asapdiscovery.data.schema.ligand import Ligand
from asapdiscovery.docking.schema.pose_generation import OpenEyeConstrainedPoseGenerator
from asapdiscovery.data.backend.openeye import save_openeye_sdfs
from pathlib import Path
import argparse

def get_args():
    parser = argparse.ArgumentParser(
        description="Generate constrained ligand poses using OpenEye tooling"
    )
    parser.add_argument(
        "--input-sdf",
        type=Path,
        required=True,
        help="Path to the multi-ligand sdf file containing the ligands to generate poses for",
    )
    parser.add_argument("--prepped-schema", type=Path, required=True, help="Path to prepped complex json schema.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=False,
        default="./",
        help="Path to the output directory where the results will be stored",
    )
    return parser.parse_args()


def main():
    args = get_args()
    args.output_dir.mkdir(exist_ok=True, parents=True)
    output_dir = args.output_dir
    raw_ligands = MolFileFactory(filename=args.input_sdf).load()

    # reconstruct ligands from smiles because of some weirdness with the sdf files
    ligs = [Ligand.from_smiles(compound_name=lig.tags['BindingDB monomerid'], smiles=lig.smiles, tags=lig.dict()) for
            lig in raw_ligands]
    prepped_complex = PreppedComplex.parse_file(args.prepped_schema)

    poser = OpenEyeConstrainedPoseGenerator()
    poses = poser.generate_poses(prepped_complex, ligands=ligs)
    oemols = [ligand.to_oemol() for ligand in poses.posed_ligands]
    # save to sdf file
    save_openeye_sdfs(oemols, output_dir / "poses.sdf")

if __name__ == "__main__":
    main()
