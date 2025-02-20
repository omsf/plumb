#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

# target is wrong but the code mostly works
# need to add loop db and might want to yank out the parts of the asap code and reproduce them here
# this automatically aligns the protein to a nonsense ASAP target, which isn't great
# it also takes an eternity to run
asap-cli protein-prep \
--target SARS-CoV-2-Mpro \
--pdb-file 3T60_BindingDB_50173539_mol_1_spruced_complex.pdb \

