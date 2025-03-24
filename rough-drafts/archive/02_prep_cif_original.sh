#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

# this is the crystallographic ligand but you wouldn't know that by this step, this needs to be fixed
python 02_prep_cif.py --input-json BindingDB_50173539_mol_1.json
