#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

asap-cli alchemy prep create -f "prep-workflow.json"

asap-cli alchemy prep run \
--factory-file prep-workflow.json \
--dataset-name 3T60_BindingDB \
--ligands 3T60_Validation_Affinities_3D.sdf \
--receptor-complex output/3T60_BindingDB_50173539_mol_1_spruced_complex-513ae159d8d9230c913ab12439d29ea53b6736e331230104a88c81607f10de65+JJJNFNLUKYZAKI-AGLMPINONA-N/3T60_BindingDB_50173539_mol_1_spruced_complex.json \
--processors 4
