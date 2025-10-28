import json
import pathlib

import click


@click.group()
def cli():
    pass


@cli.command(name="download-pdb", help="Download PDB files from the PDB database.")
@click.option("-i", "--input-file", required=True)
@click.option(
    "output_directory",
    "-d",
    "--output-directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    required=True,
)
def download_pdb_structure(input_file, output_directory):
    from asapdiscovery.data.services.rcsb.rcsb_download import download_pdb_structure

    output_directory.mkdir(exist_ok=True, parents=True)
    with open(input_file, "r") as f:
        record_dict = json.load(f)
    downloaded = download_pdb_structure(
        record_dict["pdb_id"], output_directory, file_format="cif1"
    )
    record_dict["cif"] = downloaded
    with open(output_directory / "record.json", "w") as f:
        json.dump(record_dict, f)


@cli.command(
    "assess-prepped-protein",
    help="Assess the quality of the prepped protein structure.",
)
@click.option(
    "output_directory",
    "-d",
    "--output-directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    required=True,
)
@click.option("input_openeye_du", "-i", "--input-file", type=str, required=True)
def assess_prepped_protein(output_directory, input_openeye_du):
    try:
        from openeye import oespruce
    except ModuleNotFoundError:
        raise click.UsageError("Could not import openeye")

    from asapdiscovery.data.backend.openeye import load_openeye_design_unit

    output_directory.mkdir(exist_ok=True, parents=True)

    du = load_openeye_design_unit(input_openeye_du)

    # should use a different id method
    stem = Path(input_openeye_du).stem
    validator = oespruce.OEValidateDesignUnit()
    err_msgs = validator.GetMessages(validator.Validate(du))
    sq = du.GetStructureQuality()

    report = {
        "errors": err_msgs,
        "warnings": [],
        "has_iridium_data": sq.HasIridiumData(),
    }

    with open(output_directory / f"{stem}_quality_report.json", "w") as f:
        json.dump(report, f, indent=4)


# TODO: check for openeye installation, maybe make it a decorator
@cli.command(
    "generate-constrained-ligand-poses",
    help="Generate constrained ligand poses using OpenEye tooling.",
)
@click.option("input_sdf", "-i", "--input-sdf", required=True, type=str)
@click.option("prepped_schema", "-s", "--prepped-schema", type=str)
@click.option("output_directory", "-d", "--output-directory")
def generate_constrained_ligand_poses(input_sdf, prepped_schema, output_directory):
    try:
        from asapdiscovery.data.schema.complex import PreppedComplex
        from asapdiscovery.data.readers.molfile import MolFileFactory
        from asapdiscovery.data.schema.ligand import Ligand
        from asapdiscovery.docking.schema.pose_generation import (
            OpenEyeConstrainedPoseGenerator,
        )
        from asapdiscovery.data.backend.openeye import save_openeye_sdfs
    except ModuleNotFoundError:
        raise click.UsageError("Could not import openeye")

    raw_ligands = MolFileFactory(filename=input_sdf).load()

    # reconstruct ligands from smiles because of some weirdness with the sdf files
    ligs = [
        Ligand.from_smiles(
            compound_name=lig.tags["BindingDB monomerid"],
            smiles=lig.smiles,
            tags=lig.dict(),
        )
        for lig in raw_ligands
    ]

    prepped_complex = PreppedComplex.parse_file(prepped_schema)

    poser = OpenEyeConstrainedPoseGenerator()
    poses = poser.generate_poses(prepped_complex, ligands=ligs)
    oemols = [ligand.to_oemol() for ligand in poses.posed_ligands]
    # save to sdf file
    save_openeye_sdfs(oemols, output_directory / "poses.sdf")


@cli.command("prep-cif")
def prep_cif():
    raise NotImplementedError


@cli.command("process-bindingdb")
def process_bindingdb():
    raise NotImplementedError


@cli.command("visualize-network")
def visualize_network():
    raise NotImplementedError
