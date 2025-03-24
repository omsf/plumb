#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# target is wrong but the code mostly works
# need to add loop db and might want to yank out the parts of the asap code and reproduce them here
# this automatically aligns the protein to a nonsense ASAP target, which isn't great
# it also takes an eternity to run
asap-cli protein-prep \
--target SARS-CoV-2-Mpro \
--pdb-file 3Q4B_BindingDB_50382336_mol_1_spruced_complex.pdb \

