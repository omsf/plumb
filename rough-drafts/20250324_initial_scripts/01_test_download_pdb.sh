#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

# this is the crystallographic ligand but you wouldn't know that by this step, this needs to be fixed
#python 01_download_pdb.py --input-json 00_output/BindingDB_50173539_mol_1.json --output-dir 01_output
python 01_download_pdb.py --input-json 00_output/aminoimidazo_1_2-a_pyridine.json --output-dir 01_output
