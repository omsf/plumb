#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

python 04_assess_prepped_protein.py --input-oedu output/3Q4B_BindingDB_50382336_mol_1_spruced_complex-e0627fce3796e34e880c62d46732f20f73fc7397133dc054804dbd14d6209e95+NXWASIVXQMMPLM-METULZBENA-O/3Q4B_BindingDB_50382336_mol_1_spruced_complex.oedu
