Author: Alex Payne

# 2025.02.19
I'm adding some scripts to use as a starting point.

## What I did
In general for nextflow you don't want to have to specify directories as it will arrange that for you, I mostly tried to follow that
- identified which sdf files contain ligands with 3D data
- downloaded the pdb structures corresponding to those ligands
- prepped the ligand + structure and generated design units
- assessed the structural quality of the DU

## What I didn't do and problems
- in order to use Iridium for structure quality assessment we need an mtz file, which would come from the PDB but they no longer natively host it
- I'm prepping twice in this, first in `02_prep_cif.py` and second in `03_prep_for_docking.sh`. this is because creating a DesignUnit from a prepped structure is slow and the asapdiscovery repo expects a pdb structure with a ligand in it.
- I had the "clever" idea of prepping a structure by just taking the 3D ligand coordinates and combining it with the downloaded pdb structure - this doesn't work because the BindingDB 3D coordinates are not aligned with the PDB structure. As such I think in the future we should just use the 2D sdf structure
- There isn't an obvious way to connect the ligand with the BindingDB id with the crystallographic ligand in the corresponding PDB structure. That is, for each set of ligands, I haven't found which ligand is actually the one with a real structure. The PDB usually has this information now, so we could download the PDB metadata and cross-reference that way.
- it occured to me that the asapdiscovery alchemy package has a constrained conformer generation that will be better than docking for prepping for free energy calculations. we should use it.
- I didn't include the loop_db bc it takes a long time for testing but that should happen for anything requiring simulations
-
