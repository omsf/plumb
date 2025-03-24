#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

# the idea is to eventually replace this script with nextflow

./00_test_process_bindingdb.sh
./01_test_download_pdb.sh
./02_prep_cif.sh
./03_prep_for_docking.sh
./04_assess_prepped_protein.sh
./05_generate_constrained_ligand_poses.sh
./06_make_fec_inputs.sh

# since this uses significant compute, lets not run by default
# ./07_submit_to_alchemiscale.sh
