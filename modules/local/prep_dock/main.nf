#!/usr/bin/env nextflow

// Module written by Alex Payne
// https://github.com/choderalab/openproteinsim/blob/20241002_plinder/science/20241002_plinder/nextflow_scripts/modules.nf
process PROCESS_INPUT {
    publishDir 'results', mode: 'copy', overwrite: true

    conda "/home/brennera/miniconda3/envs/asapdiscovery" // conda-forge::asapdiscovery
    // tag "process_input"
    // clusterOptions '--partition cpushort'

    output:
    //path("*.json"), emit: input_files
    path("*.csv"), emit: input_files

    script:
    """
    echo "Checking Conda environment..."
    conda info --envs  # List environments
    echo "Current Python path: \$(which python)"
    echo "Current Conda environment: \$CONDA_PREFIX"
    
    conda list  # Show installed packages
    python -c "import pyarrow; print('pyarrow is available')"
    python ${projectDir}/bin/00_process_input.py "${params.pdbDatabase}" "${params.structureParquet}"
    """
}