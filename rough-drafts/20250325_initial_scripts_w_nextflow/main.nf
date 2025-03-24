#!/usr/bin/env nextflow
params.projectDir = "/data1/choderaj/paynea/plumb/rough-drafts/20250325_initial_scripts_w_nextflow"
params.scripts = "${params.projectDir}/bin"
params.bindingDB = "/data1/choderaj/paynea/plumb_binding_db/BindingDBValidationSets-1"

// Conda Envs
params.asap = "/home/paynea/miniforge3/envs/asap2025"

/*
 * Define the workflow
 */
include {
PROCESS_BINDINGDB
} from "./modules.nf"

workflow {
    PROCESS_BINDINGDB()
}
