import json
import pathlib

import click


@click.group()
def cli():
    pass


# TODO: input file type can be better defined
@cli.command(name="download-pdb", help="Download PDB files from the PDB database.")
@click.option("-i", "--input-file", type=str, required=True)
@click.option(
    "output_directory",
    "-o",
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
    "-o",
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
    stem = pathlib.Path(input_openeye_du).stem
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
@click.option(
    "output_directory",
    "-o",
    "--output-directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    required=True,
)
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
@click.option("input_json", "-j", "--input-json", type=str, required=True)
@click.option("input_cif", "-c", "--input-cif", type=str, required=True)
@click.option(
    "fasta_sequence", "-f", "--fasta-sequence", type=str, default=None, required=True
)
@click.option("loop_db", "--loopdb", type=str, required=True)
@click.option(
    "output_directory",
    "-o",
    "--output-directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    default="./",
    required=True,
)
def prep_cif(input_json, input_cif, fasta_sequence, loop_db, output_directory):
    from asapdiscovery.data.backend.openeye import load_openeye_cif1
    from asapdiscovery.modeling.modeling import split_openeye_mol
    from asapdiscovery.data.schema.ligand import Ligand, Complex
    from plumbdb.oespruce import spruce_protein
    from asapdiscovery.data.schema.target import Target

    output_directory.mkdir(exist_ok=True, parents=True)

    with open(input_json, "r") as f:
        record_dict = json.load(f)

    graphmol = load_openeye_cif1(input_cif)

    # this is what you would do if you didn't want to use whatever ligand is in the protein
    # split_dict = split_openeye_mol(graphmol, keep_one_lig=False)
    split_dict = split_openeye_mol(graphmol, keep_one_lig=True)

    # # Save initial protein as pdb file
    target = Target.from_oemol(
        split_dict["prot"],
        target_name=record_dict["pdb_id"],
    )
    # target.to_pdb("protein.pdb")

    # this is what you would do if you didn't want to use whatever ligand is in the protein
    ligand = Ligand.from_oemol(split_dict["lig"])
    # ligand = Ligand.from_sdf(f'{record_dict["compound_name"]}.sdf')

    combined_complex = Complex(target=target, ligand=ligand, ligand_chain="L")

    oemol = combined_complex.to_combined_oemol()

    results, spruced = spruce_protein(
        initial_prot=oemol,
        protein_sequence=fasta_sequence,
        loop_db=loop_db,
    )

    split_dict = split_openeye_mol(spruced)
    prepped_target = Target.from_oemol(split_dict["prot"], **target.dict())
    prepped_ligand = Ligand.from_oemol(split_dict["lig"], **ligand.dict())
    prepped_ligand.to_sdf(output_directory / f"{ligand.compound_name}_ligand.sdf")
    prepped_target.to_pdb(output_directory / f"{target.target_name}_spruced.pdb")

    prepped_complex = Complex(
        target=prepped_target, ligand=prepped_ligand, ligand_chain="L"
    )

    filename = f"{target.target_name}_{ligand.compound_name}_spruced_complex.pdb"
    prepped_complex.to_pdb(output_directory / filename)
    results.to_json_file(output_directory / f"{target.target_name}_spruce_results.json")


# TODO: help string
@cli.command(
    "process-bindingdb", help="Parse and verify SDF files downloaded from bindingdb."
)
@click.option(
    "input_directory",
    "-i",
    "--input-directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    required=True,
    help="SDF file to process",
)
@click.option(
    "output_directory",
    "-o",
    "--output-directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    required=True,
    help="Directory to write output files",
)
def process_bindingdb(input_directory, output_directory):
    from asapdiscovery.data.schema.ligand import Ligand
    from asapdiscovery.data.readers.molfile import MolFileFactory
    import pandas as pd
    import math

    output_directory.mkdir(exist_ok=True, parents=True)

    # get all sdf files
    sdfs = list(input_directory.glob("*3D.sdf"))

    output = []
    for sdf in sdfs:
        # asap function to read separate ligands from a multi-ligand sdf file
        mols: list[Ligand] = MolFileFactory(filename=sdf).load()

        # create a dictionary for each ligand containing various relevant information
        # there are some hidden choices here, for instance OpenEye is adding hydrogens which you might not want

        for mol in mols:
            mol_dict = {
                "compound_name": mol.compound_name,
                "filename": sdf.name,
                "has_3d": mol.to_oemol().GetDimension() == 3,
                "num_atoms": mol.to_oemol().NumAtoms(),
                "smiles": mol.smiles,
                "pdb_id": mol.tags.get("PDB ID ")[:4]
                if mol.tags.get("PDB ID ")
                else "",
            }

            # any data in the SDF file is saved to the 'tags' attribute of an asapdiscovery Ligand object
            mol_dict.update(mol.tags)

            # write out sdf file
            if mol_dict["has_3d"]:
                mol.to_sdf(output_directory / f"{mol.compound_name}.sdf")

            output.append(mol_dict)

    df = pd.DataFrame.from_records(output)
    df.to_csv(output_directory / "processed_bindingdb.csv", index=False)

    # write separate csvs for 2D and 3D
    df_2d = df[~df["has_3d"]]
    df_3d = df[df["has_3d"]]
    df_2d.to_csv(output_directory / "2d_bindingdb.csv", index=False)
    df_3d.to_csv(output_directory / "3d_bindingdb.csv", index=False)

    unique_sdf_filenames = df_3d["filename"].unique()
    with open(output_directory / "unique_3D_sdf_filenames.txt", "w") as f:
        for filename in unique_sdf_filenames:
            f.write(f"{filename}\n")

    # write out separate json records
    for record in df_3d.to_dict(orient="records"):
        with open(output_directory / f"{record['compound_name']}.json", "w") as f:
            f.write(
                json.dumps(
                    record, indent=4, default=lambda x: None if math.isnan(x) else x
                )
            )


@cli.command(
    "visualize-network",
    help="Generate a network plot of the proposed alchemical network",
)
@click.option(
    "network_graphml",
    "-n",
    "--network-graphml",
    type=str,
    required=True,
    help="Path to the input JSON file containing the atom mapping network.",
)
@click.option(
    "output_directory",
    "-o",
    "--output-directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    required=True,
    default=pathlib.Path("./"),
    help="Path to the output directory where the results will be stored",
)
def visualize_network(network_graphml, output_directory):
    from openfe.utils.atommapping_network_plotting import plot_atommapping_network
    from openfe.setup import LigandNetwork

    output_directory.mkdir(exist_ok=True, parents=True)
    ligand_network = network_graphml

    if not ligand_network.exists():
        raise FileNotFoundError(
            f"Could not find the ligand network file at {ligand_network}"
        )

    with open(ligand_network) as f:
        graphml = f.read()

    network = LigandNetwork.from_graphml(graphml)
    fig = plot_atommapping_network(network)
    fig.savefig(output_directory / "network_plot.png")
