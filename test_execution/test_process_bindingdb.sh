#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# put your own path to the bindingdb directory here
python ../bin/process_bindingdb.py --input-dir ../raw_data/binding_db
