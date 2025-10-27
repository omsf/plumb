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
        record_dict["pdb_id"], output_dir, file_format="cif1"
    )
    record_dict["cif"] = downloaded
    with open(output_dir / "record.json", "w") as f:
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
