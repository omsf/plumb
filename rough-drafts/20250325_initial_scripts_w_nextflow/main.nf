#!/usr/bin/env nextflow
import groovy.json.JsonSlurper
params.projectDir = "/data1/choderaj/paynea/plumb/rough-drafts/20250325_initial_scripts_w_nextflow"
params.scripts = "${params.projectDir}/bin"
params.bindingDB = "/data1/choderaj/paynea/plumb_binding_db/BindingDBValidationSets-1/test"
// hacky way to get around needing to learn to read FASTA from cif
params.fasta = "MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNHPNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCHSHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKYYSTAVDIWSLGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPSFPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL"
params.output = "${params.bindingDB}/output"

// Conda Envs
params.asap = "/home/paynea/miniforge3/envs/asap2025"

// Flags
params.take = -1

/*
 * Define the workflow
 */
include {
PROCESS_BINDINGDB;
DOWNLOAD_PDB;
PREP_CIF;
PREP_FOR_DOCKING
} from "./modules.nf"

workflow {
    PROCESS_BINDINGDB()
    input_files = PROCESS_BINDINGDB.out.input_json.flatten().take(params.take)

    // Load in input json files and extract unique id from each and connect it to the json
    input_files.map{json ->  tuple([new JsonSlurper().parseText(json.text)][0].get("BindingDB monomerid"), json)}
        .set{unique_jsons}
    // Only download one for testing
//     DOWNLOAD_PDB(unique_jsons.filter{value -> value[0] == "6702"})
    DOWNLOAD_PDB(unique_jsons)
    PREP_CIF(DOWNLOAD_PDB.out.input_cif.combine(DOWNLOAD_PDB.out.record_json, by:0))
    PREP_FOR_DOCKING(PREP_CIF.out.prepped_pdb)
}
