#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

mkdir -p 06_output
asap-cli alchemy create 06_output/fecs-workflow.json

asap-cli alchemy plan \
-f 06_output/fecs-workflow.json \
--name 1YKR_BindingDB \
--receptor 03_output/1YKR_628_spruced_complex-e451b175abc59819098c134cd56f9be042e5caccb1d498b70bcd7620ac0b1fa4+UQAWGIKJINAKIZ-TWSYTRIPNA-N/1YKR_628_spruced_complex.pdb \
--ligands 05_output/poses.sdf \

# the resulting network can be analyzed by running this command in the folder 1YKR_BindingDB:
# openfe view-ligand-network ligand_network.graphml
