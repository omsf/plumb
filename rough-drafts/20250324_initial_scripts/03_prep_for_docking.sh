#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

# target is wrong but the code mostly works
# need to add loop db and might want to yank out the parts of the asap code and reproduce them here
# this automatically aligns the protein to a nonsense ASAP target, which isn't great
# it also takes an eternity to run
asap-cli protein-prep \
--target SARS-CoV-2-Mpro \
--pdb-file 02_output/1YKR_628_spruced_complex.pdb \
--output-dir 03_output

