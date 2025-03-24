"""
Assess the quality of the prepped protein structure
"""

import argparse
from openeye import oespruce
from asapdiscovery.data.backend.openeye import load_openeye_design_unit
from pathlib import Path
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-oedu",
        type=Path,
        help="Path to input CIF file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="./",
        help="Path to the output directory.",)
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    du = load_openeye_design_unit(args.input_oedu)

    # should use a different id method
    stem = Path(args.input_oedu).stem
    validator = oespruce.OEValidateDesignUnit()
    err_msgs = validator.GetMessages(validator.Validate(du))
    sq = du.GetStructureQuality()

    report = {'errors': err_msgs, 'warnings': [], 'has_iridium_data': sq.HasIridiumData()}

    with open(output_dir / f"{stem}_quality_report.json", "w") as f:
        json.dump(report, f, indent=4)


if __name__ == "__main__":
    main()
