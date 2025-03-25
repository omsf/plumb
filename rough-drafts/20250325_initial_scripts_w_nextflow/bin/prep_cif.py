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
import requests
import re


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-json",
    )
    parser.add_argument("--input-cif", type=Path, help="Path to input CIF file")
    parser.add_argument("--loop-db", type=Path, help="Path to loop database")
    parser.add_argument("--output-dir", type=Path, default="./", help="Path to the output directory.")
    return parser.parse_args()


class SpruceResults(DataModelAbstractBase):
    build_loops_success: bool
    build_sidechains_success: bool
    add_caps_success: bool = None
    place_hydrogens_success: bool
    error_message: str


def protein_sequence_from_fasta(pdb_id) -> dict[str, str]:
    """
    Download FASTA sequence for a given PDB ID.

    Parameters
    ----------
    pdb_id : str
        The PDB identifier (e.g., '1ABC')

    Returns
    -------
    str
        The protein sequence as a string
    """
    # PDB FASTA file URL
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id}/download"

    try:
        # Send GET request to download FASTA
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the FASTA content
        fasta_lines = response.text.split('\n')

        # Parse the headers
        header_lines = [(i, line) for i, line in enumerate(fasta_lines) if line.startswith('>')]
        protein_sequence_dict = {}

        for n, (idx, header) in enumerate(header_lines):
            # Extract chains using regex
            chain_match = re.search(r'Chains?\s*([A-Z,\s]+)\|', header)
            if chain_match:
                # Split and clean chain names
                chains = chain_match.group(1).replace(' ', '').split(',')

                # Handle the last header separately
                if n == len(header_lines) - 1:
                    # If it's the last header, go to the end of the file
                    sequence_lines = [line.strip() for line in fasta_lines[idx + 1:] if line.strip()]
                else:
                    # For other headers, use the next header's index
                    sequence_lines = [line.strip() for line in fasta_lines[idx + 1:header_lines[n + 1][0]] if
                                      line.strip()]

                protein_sequence = " ".join(convert_to_three_letter_codes(''.join(sequence_lines)))
                protein_sequence_dict.update({chain: protein_sequence for chain in chains})

        return protein_sequence_dict

    except requests.RequestException as e:
        print(f"Error downloading FASTA for PDB ID {pdb_id}: {e}")
        raise e

def get_protein_chains(mol: oechem.OEGraphMol):
    """
    Get the protein chains from an OpenEye molecule.
    Args:
        mol:

    Returns:

    """
    return {res.GetChainID() for res in oechem.OEGetResidues(mol) if oechem.OEIsStandardProteinResidue(res)}

def get_oe_structure_metadata_from_sequence_dict(mol: oechem.OEGraphMol, sequence_dict: dict[str, str]) -> oespruce.OEStructureMetadata:
    """
    Read FASTA file and add sequence to structure metadata
    :param mol:
    :param fasta_path:
    :return:
    """
    metadata = oespruce.OEStructureMetadata()
    all_prot_chains = get_protein_chains(mol)
    for chain in all_prot_chains:
        seq_metadata = oespruce.OESequenceMetadata()
        seq_metadata.SetChainID(chain)
        seq_metadata.SetSequence(sequence_dict[chain])
        metadata.AddSequenceMetadata(seq_metadata)
    return metadata

def spruce_protein(
    initial_prot: oechem.OEGraphMol,
    protein_sequence: dict,
    loop_db: Path,
) -> oechem.OEDesignUnit or oechem.OEGraphMol:
    """
    Applies the OESpruce protein preparation pipeline to the given protein structure.

    Parameters
    ----------
    initial_prot : oechem.OEMol
        The input protein structure to be prepared.

    protein_sequence : dict
        The sequence of the protein for a single chain. This is will be added to the Structure Metadata before applying the OESpruce pipeline.

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
    cap_opts = oespruce.OECapBuilderOptions()
    cap_opts.SetAllowTruncate(True)
    is_terminal_predicate = oechem.OEOrAtom(
        oechem.OEIsNTerminalAtom(), oechem.OEIsCTerminalAtom()
    )

    # Set Build Loop and Sidechain Opts
    sc_opts = oespruce.OESidechainBuilderOptions()

    loop_opts = oespruce.OELoopBuilderOptions()
    loop_opts.SetSeqAlignMethod(oechem.OESeqAlignmentMethod_Identity)
    loop_opts.SetSeqAlignGapPenalty(-1)
    loop_opts.SetSeqAlignExtendPenalty(0)
    loop_opts.SetLoopDBFilename(str(loop_db))

    # Don't build tails, too much work for little gain
    loop_opts.SetBuildTails(False)

    metadata = get_oe_structure_metadata_from_sequence_dict(initial_prot, protein_sequence)

    # Construct spruce filter
    grid = oegrid.OESkewGrid()
    spruce_opts = oespruce.OESpruceFilterOptions()
    spruce = oespruce.OESpruceFilter(spruce_opts, opts)

    ret_filter = spruce.StandardizeAndFilter(initial_prot, grid, metadata)
    if ret_filter != oespruce.OESpruceFilterIssueCodes_Success:
        oechem.OEThrow.Warning("This structure fails spruce filter due to: ")
        oechem.OEThrow.Warning(spruce.GetMessages())
        oechem.OEThrow.Fatal("This structure fails spruce filter")

    build_loops_success = oespruce.OEBuildLoops(
        initial_prot, metadata, sc_opts, loop_opts
    )

    build_sidechains_success = oespruce.OEBuildSidechains(initial_prot, sc_opts)
    add_caps_success = oespruce.OECapTermini(initial_prot, is_terminal_predicate, cap_opts)
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

    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    with open(args.input_json, "r") as f:
        record_dict = json.load(f)

    pdbid = record_dict['pdb_id']

    graphmol = load_openeye_cif1(args.input_cif)

    # this is what you would do if you didn't want to use whatever ligand is in the protein
    # split_dict = split_openeye_mol(graphmol, keep_one_lig=False)
    split_dict = split_openeye_mol(graphmol, keep_one_lig=True)

    # Get initial protein as pdb file
    target = Target.from_oemol(
        split_dict["prot"],
        target_name=pdbid,
    )

    # this is what you would do if you didn't want to use whatever ligand is in the protein
    ligand = Ligand.from_oemol(split_dict["lig"])

    combined_complex = Complex(target=target, ligand=ligand, ligand_chain="L")

    oemol = combined_complex.to_combined_oemol()

    # pull protein sequence from fasta data
    protein_sequence = protein_sequence_from_fasta(pdbid)

    # spruce protein
    results, spruced = spruce_protein(
        initial_prot=oemol,
        protein_sequence=protein_sequence,
        loop_db=args.loop_db,
    )
    split_dict = split_openeye_mol(spruced)
    prepped_target = Target.from_oemol(split_dict["prot"], **target.dict())
    prepped_ligand = Ligand.from_oemol(split_dict["lig"], **ligand.dict())
    prepped_ligand.to_sdf(output_dir / f"{ligand.compound_name}_ligand.sdf")
    prepped_target.to_pdb(output_dir / f"{target.target_name}_spruced.pdb")

    prepped_complex = Complex(target=prepped_target, ligand=prepped_ligand, ligand_chain="L")
    prepped_complex.to_pdb(output_dir / f"{target.target_name}_{ligand.compound_name}_spruced_complex.pdb")
    results.to_json_file(output_dir / f"{target.target_name}_spruce_results.json")


if __name__ == "__main__":
    main()
