#!/usr/bin/env nextflow 

// Import essential data

process DOWNLOAD_BINDINGDB {
    publishDir "${projectDir}/raw_data", mode: 'copy', overwrite: true

    conda "conda-forge::unzip"

    output:
    path "BindingDBValidationSets-1.zip", emit: raw_data_zip

    script:
    """
    mkdir -p ${projectDir}/raw_data
    curl -L -o BindingDBValidationSets-1.zip "https://www.bindingdb.org/rwd/bind/downloads/BindingDBValidationSets-1.zip"
    unzip -o BindingDBValidationSets-1.zip -d ${projectDir}/raw_data/binding_db
    """
}

// process PROCESS_BINDINGDB {
//     publishDir "${projectDir}/intermed_data", mode: 'copy', overwrite: true

//     conda "/home/brennera/miniconda3/envs/asapdiscovery"

//     output:
//     path "BindingDBValidationSets-1.zip", emit: raw_data_zip

//     script:
//     """
//     mkdir -p ${projectDir}/intermed_data
//     python ${projectDir}/bin/process_bindingdb.py --input-dir ${projectDir}/raw_data/binding_db
//     """
// }

process PROCESS_BINDINGDB {

    /**
    * PROCESS: PROCESS_BINDINGDB
    * -----------------------------------------
    * This process:
    * - Takes an input directory containing SDF files
    * - Runs a Python script (`process_bindingdb.py`) to process them
    * - Outputs multiple processed CSV and JSON files
    * 
    * Environment:
    * - Uses an existing Conda environment (`asapdiscovery`)
    * - Runs on SLURM with specified resources
    * 
    * TO DO: 
    * The conda directive does not seem to work. I need to 
    * manually activate the environment of interest and I am not sure why
    * this is not ideal but ok for development. 
    */

    tag "process_bindingdb"
    conda "/home/brennera/miniconda3/envs/asapdiscovery"
    
    // publishDir file(projectDir) / "intermed_data", mode: 'copy', overwrite: true
    publishDir file("${projectDir}/intermed_data"), mode: 'copy', overwrite: true

    input:
    path input_dir // The directory containing the SDF files

    output:
    path "processed_bindingdb.csv"
    path "2d_bindingdb.csv"
    path "3d_bindingdb.csv"
    path "unique_3D_sdf_filenames.txt"
    path "*.json"
    path "*.sdf"
    
    script:
    """
    source /home/brennera/miniconda3/etc/profile.d/conda.sh 
    conda activate asapdiscovery 
    which python
    python ${projectDir}/bin/process_bindingdb.py --input-dir ${input_dir}
    """
}