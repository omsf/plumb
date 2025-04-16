"""
Generate a network plot of the proposed alchemical network
"""

import argparse
from pathlib import Path
from openfe.utils.atommapping_network_plotting import (
        plot_atommapping_network
    )
from openfe.setup import LigandNetwork

def get_args():
    parser = argparse.ArgumentParser(
        description="Generate a network plot of the proposed alchemical network"
    )
    parser.add_argument("-n",
        "--network-graphml",
        type=Path,
        required=True,
        help="Path to the input JSON file containing the atom mapping network. ",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=False,
        default="./",
        help="Path to the output directory where the results will be stored",
    )
    return parser.parse_args()

def main():
    args = get_args()
    output_dir = args.output
    output_dir.mkdir(exist_ok=True, parents=True)

    ligand_network = args.network_graphml
    if not ligand_network.exists():
        raise FileNotFoundError(f"Could not find the ligand network file at {ligand_network}")

    with open(ligand_network) as f:
        graphml = f.read()

    network = LigandNetwork.from_graphml(graphml)
    fig = plot_atommapping_network(network)
    fig.savefig(output_dir / "network_plot.png")


if __name__ == "__main__":
    main()
