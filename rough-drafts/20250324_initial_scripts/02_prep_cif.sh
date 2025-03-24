#!/bin/zsh
source ~/.zshrc
mamba activate asap2025

# this is the crystallographic ligand but you wouldn't know that by this step, this needs to be fixed
python 02_prep_cif.py \
--input-json 01_output/record.json \
--loop-db ~/rcsb_spruce.loop_db \
--fasta-sequence MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNHPNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCHSHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKYYSTAVDIWSLGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPSFPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL \
--output-dir 02_output

# got the fasta sequence from the rcsb fasta download
# no idea how this will work for multidomain targets with heterogenous domains
