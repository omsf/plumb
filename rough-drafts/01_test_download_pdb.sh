#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# this is the crystallographic ligand but you wouldn't know that by this step, this needs to be fixed
# Not seeing this code alex selected, starting with different one
# python 01_download_pdb.py --input-json BindingDB_50173539_mol_1.json
python 01_download_pdb.py --input-json BindingDB_50382336_mol_1.json
