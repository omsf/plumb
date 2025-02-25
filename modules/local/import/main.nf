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
    which python
    python ${projectDir}/bin/process_bindingdb.py --input-dir ${input_dir}
    """
}