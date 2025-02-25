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


// process DOWNLOAD_BINDINGDB {
//     publishDir "${projectDir}/raw_data", mode: 'copy', overwrite: true

//     output:
//     path "binding_db/", emit: raw_data_folder
//     path "binding_db/README.txt", emit: readme_file

//     script:
//     """
//     # Create directories
//     mkdir -p ${projectDir}/raw_data/binding_db

//     # Download the dataset using curl
//     curl -L -o BindingDBValidationSets-1.zip "https://www.bindingdb.org/bind/chemsearch/marvin/SDFdownload.jsp?download_file=/bind/downloads/BindingDBValidationSets-1.zip"

//     # Unzip into the binding_db directory
//     unzip -o BindingDBValidationSets-1.zip -d ${projectDir}/raw_data/binding_db

//     # Create a README file with timestamp
//     echo "BindingDB dataset downloaded on: \$(date)" > ${projectDir}/raw_data/binding_db/README.txt

//     # Remove the original ZIP file to save space
//     rm BindingDBValidationSets-1.zip
//     """
// }
