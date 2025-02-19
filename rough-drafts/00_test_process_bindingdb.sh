#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

# put your own path to the bindingdb directory here
python 00_process_bindingdb.py --input-dir /Users/alexpayne/Downloads/BindingDBValidationSets-1
