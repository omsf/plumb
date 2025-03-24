import argparse
from pathlib import Path
from asapdiscovery.data.schema.schema_base import DataModelAbstractBase
from asapdiscovery.data.backend.openeye import (
    oespruce,
    oechem,
    oegrid,
    load_openeye_cif1,
)
from asapdiscovery.modeling.modeling import (
    split_openeye_mol,
    spruce_protein,
    get_oe_structure_metadata_from_sequence,
    openeye_perceive_residues,
)
from asapdiscovery.data.schema.target import Target
from asapdiscovery.data.schema.ligand import Ligand
import json
from asapdiscovery.data.schema.complex import Complex


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-json",
    )
    parser.add_argument("--loop-db", type=Path, help="Path to loop database")
    return parser.parse_args()


class SpruceResults(DataModelAbstractBase):
    build_loops_success: bool
    build_sidechains_success: bool
    add_caps_success: bool = None
    place_hydrogens_success: bool
    error_message: str


def spruce_protein(
    initial_prot: oechem.OEGraphMol,
    protein_sequence: str = None,
    loop_db: Path = None,
) -> oechem.OEDesignUnit or oechem.OEGraphMol:
    """
    Applies the OESpruce protein preparation pipeline to the given protein structure.

    Parameters
    ----------
    initial_prot : oechem.OEMol
        The input protein structure to be prepared.

    protein_sequence : str, optional
        The sequence of the protein for a single chain. If provided, this will be added to the Structure Metadata before applying the OESpruce pipeline.
        Default is None.

    loop_db : str, optional
        The filename of the loop database to be used by the OESpruce pipeline. If provided, the pipeline will include the loop building step.
        Default is None.

    Returns
    -------
    (success: bool, spruce_error_msg: str, initial_prot: oechem.OEMol)
        Returns a tuple of:
        a boolean for whether sprucing was successful
        a string of the error message if sprucing failed
        the prepared protein structure.
    """

    # Add Hs to prep protein and ligand
    # oechem.OEAddExplicitHydrogens(initial_prot)

    # Even though we aren't making DUs, we still need to set up the options
    opts = oespruce.OEMakeDesignUnitOptions()
    opts.SetSuperpose(False)
    opts.GetPrepOptions().SetStrictProtonationMode(True)

    # Add caps when needed
    # Allow truncation in case adding a cap causes a clash
    # cap_opts = oespruce.OECapBuilderOptions()
    # # cap_opts.SetCap
    # cap_opts.SetAllowTruncate(False)
    # is_terminal_predicate = oechem.OEOrAtom(
    #     oechem.OEIsNTerminalAtom(), oechem.OEIsCTerminalAtom()
    # )

    # Set Build Loop and Sidechain Opts
    sc_opts = oespruce.OESidechainBuilderOptions()

    loop_opts = oespruce.OELoopBuilderOptions()
    loop_opts.SetSeqAlignMethod(oechem.OESeqAlignmentMethod_Identity)
    loop_opts.SetSeqAlignGapPenalty(-1)
    loop_opts.SetSeqAlignExtendPenalty(0)

    # Don't build tails, too much work for little gain
    loop_opts.SetBuildTails(False)

    if loop_db is not None:
        print(f"Adding loop db {loop_db}")
        loop_opts.SetLoopDBFilename(str(loop_db))

    # Construct spruce filter
    spruce_opts = oespruce.OESpruceFilterOptions()
    spruce = oespruce.OESpruceFilter(spruce_opts, opts)

    # Spruce!

    # These objects are for some reason needed in order to run spruce
    grid = oegrid.OESkewGrid()

    if protein_sequence:
        # convert fasta sequence to 3-letter codes
        try:
            protein_sequence = " ".join(convert_to_three_letter_codes(protein_sequence))
            print(type(protein_sequence))
            print("Adding sequence metadata from sequence: ", protein_sequence)
            metadata = get_oe_structure_metadata_from_sequence(
                initial_prot, protein_sequence
            )
        except KeyError as e:
            print(
                f"Error converting protein sequence to 3-letter codes: {e}. Skipping sequence metadata."
            )
            protein_sequence = None

    if not protein_sequence:
        metadata = oespruce.OEStructureMetadata()

    # Building the loops actually does use the sequence metadata
    build_loops_success = oespruce.OEBuildLoops(
        initial_prot, metadata, sc_opts, loop_opts
    )

    build_sidechains_success = oespruce.OEBuildSidechains(initial_prot, sc_opts)
    # print(type(initial_prot), type(is_terminal_predicate), type(cap_opts))
    # add_caps_success = oespruce.OECapTermini(initial_prot)
    place_hydrogens_success = oechem.OEPlaceHydrogens(initial_prot)
    spruce_error_code = spruce.StandardizeAndFilter(initial_prot, grid, metadata)
    spruce_error_msg = spruce.GetMessages(spruce_error_code)

    # Re-percieve residues so that atom number and connect records dont get screwed up
    initial_prot = openeye_perceive_residues(initial_prot, preserve_all=False)
    return (
        SpruceResults(
            build_loops_success=build_loops_success,
            build_sidechains_success=build_sidechains_success,
            # add_caps_success=None,  # add_caps_success,
            place_hydrogens_success=place_hydrogens_success,
            error_message=spruce_error_msg,
        ),
        initial_prot,
    )


def convert_to_three_letter_codes(sequence) -> list[str]:
    """
    Convert a protein sequence from 1-letter codes to 3-letter codes.
    """
    # Dictionary to map 1-letter codes to 3-letter codes
    amino_acid_dict = {
        "A": "ALA",
        "R": "ARG",
        "N": "ASN",
        "D": "ASP",
        "C": "CYS",
        "Q": "GLN",
        "E": "GLU",
        "G": "GLY",
        "H": "HIS",
        "I": "ILE",
        "L": "LEU",
        "K": "LYS",
        "M": "MET",
        "F": "PHE",
        "P": "PRO",
        "S": "SER",
        "T": "THR",
        "W": "TRP",
        "Y": "TYR",
        "V": "VAL",
    }

    # Convert the sequence to 3-letter codes
    three_letter_sequence = [amino_acid_dict[aa] for aa in sequence]

    # Join the 3-letter codes with a space
    return three_letter_sequence


def main():
    args = parse_args()

    with open(args.input_json, "r") as f:
        record_dict = json.load(f)

    graphmol = load_openeye_cif1(record_dict['cif'])

    # this is what you would do if you didn't want to use whatever ligand is in the protein
    # split_dict = split_openeye_mol(graphmol, keep_one_lig=False)

    # # Save initial protein as pdb file
    # target = Target.from_oemol(
    #     split_dict["prot"],
    #     target_name=record_dict['pdb_id'],
    # )

    target = Target.from_oemol(graphmol, target_name=record_dict['pdb_id'])

    target.to_pdb("protein.pdb")

    ligand = Ligand.from_sdf(f'{record_dict["compound_name"]}.sdf')

    combined_complex = Complex(target=target, ligand=ligand, ligand_chain="L")

    oemol = combined_complex.to_combined_oemol()

    # spruce protein
    results, spruced = spruce_protein(
        initial_prot=oemol,
        # protein_sequence=old_record.sequence,
        loop_db=args.loop_db,
    )
    split_dict = split_openeye_mol(spruced)
    prepped_target = Target.from_oemol(split_dict["prot"], **target.dict())
    prepped_ligand = Ligand.from_oemol(split_dict["lig"], **ligand.dict())
    prepped_ligand.to_sdf(f"{ligand.compound_name}_ligand.sdf")
    prepped_target.to_pdb(f"{target.target_name}_spruced.pdb")

    prepped_complex = Complex(target=prepped_target, ligand=prepped_ligand, ligand_chain="L")
    prepped_complex.to_pdb(f"{target.target_name}_{ligand.compound_name}_spruced_complex.pdb")
    results.to_json_file(f"{target.target_name}_spruce_results.json")


if __name__ == "__main__":
    main()
