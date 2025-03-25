#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# this requires alchemiscale key, etc
asap-cli alchemy submit \
--network 1YKR_BindingDB/planned_network.json \
--organization choderalab \
--campaign 'plumb' \
--project 'bindingdb'

# results of this job can be checked by running this command in the folder 1YKR_BindingDB:
# asap-cli alchemy status

# to pull down the results, run this command in the folder 1YKR_BindingDB:
# asap-cli alchemy gather
