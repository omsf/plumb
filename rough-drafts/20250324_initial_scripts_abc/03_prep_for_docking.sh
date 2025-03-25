#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# target is wrong but the code mostly works
# need to add loop db and might want to yank out the parts of the asap code and reproduce them here
# this automatically aligns the protein to a nonsense ASAP target, which isn't great
# it also takes an eternity to run
asap-cli protein-prep \
--target SARS-CoV-2-Mpro \
--pdb-file 02_output/3D8W_D8W_spruced_complex.pdb \
--output-dir 03_output

echo "done"

