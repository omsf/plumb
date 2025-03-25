#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# put your own path to the bindingdb directory here
python 00_process_bindingdb.py --input-dir ../../raw_data/binding_db --output-dir 00_output
