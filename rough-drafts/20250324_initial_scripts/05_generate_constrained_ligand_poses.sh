#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

python 05_generate_constrained_ligand_poses.py \
--input-sdf /Users/alexpayne/Downloads/BindingDBValidationSets-1/1YKR_Validation_Affinities_3D.sdf \
--prepped-schema 03_output/1YKR_628_spruced_complex-e451b175abc59819098c134cd56f9be042e5caccb1d498b70bcd7620ac0b1fa4+UQAWGIKJINAKIZ-TWSYTRIPNA-N/1YKR_628_spruced_complex.json \
--output-dir 05_output
