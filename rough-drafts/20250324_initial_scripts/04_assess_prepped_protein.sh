#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

python 04_assess_prepped_protein.py --input-oedu 03_output/1YKR_628_spruced_complex-e451b175abc59819098c134cd56f9be042e5caccb1d498b70bcd7620ac0b1fa4+UQAWGIKJINAKIZ-TWSYTRIPNA-N/1YKR_628_spruced_complex.oedu \
--output-dir 04_output
