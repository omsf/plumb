#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

python 04_assess_prepped_protein.py --input-oedu 03_output/3D8W_D8W_spruced_complex-bc7403f1b5ce117979797732be9b22cdef6a675fe1f2916e5fa235550f0579ce+PWDGTQXZLNDOKS-TVNKGWMHNA-N/3D8W_D8W_spruced_complex.oedu \
--output-dir 04_output
