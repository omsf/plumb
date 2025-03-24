#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# this is the crystallographic ligand but you wouldn't know that by this step, this needs to be fixed
python 02_prep_cif.py --input-json BindingDB_50382336_mol_1.json
