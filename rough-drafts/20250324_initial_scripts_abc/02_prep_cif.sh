#!/bin/bash
source ${HOME}/.bashrc
conda activate asapdiscovery

# this is the crystallographic ligand but you wouldn't know that by this step, this needs to be fixed
python 02_prep_cif.py \
--input-json 01_output/record.json \
--loop-db ~/rcsb_spruce.loop_db \
--fasta-sequence MSHHWGYGKHNGPEHWHKDFPIAKGERQSPVDIDTHTAKYDPSLKPLSVSYDQATSLRILNNGHAFNVEFDDSQDKAVLKGGPLDGTYRLIQFHFHWGSLDGQGSEHTVDKKKYAAELHLVHWNTKYGDFGKAVQQPDGLAVLGIFLKVGSAKPGLQKVVDVLDSIKTKGKSADFTNFDPRGLLPESLDYWTYPGSLTTPPLLECVTWIVLKEPISVSSEQVLKFRKLNFNGEGEPEELMVDNWRPAQPLKNRQIKASFK \
--output-dir 02_output


# Print "done" at the end
echo "done"
# got the fasta sequence from the rcsb fasta download
# no idea how this will work for multidomain targets with heterogenous domains
