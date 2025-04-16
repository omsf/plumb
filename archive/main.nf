#!/usr/bin/env nextflow
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    nf-core/plumb
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Github : https://github.com/nf-core/plumb
    Website: https://nf-co.re/plumb
    Slack  : https://nfcore.slack.com/channels/plumb
----------------------------------------------------------------------------------------
*/


/*
Need to move these params to config file
*/
params.pdbDatabase = "/data1/choderaj/paynea/openproteinsim_plinder/test_set_26092024/combined"
params.structureParquet = "/data1/choderaj/paynea/openproteinsim_plinder/test_set_26092024/info.parquet"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT FUNCTIONS / MODULES / SUBWORKFLOWS / WORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { PLUMB  } from './workflows/plumb'
include { PIPELINE_INITIALISATION } from './subworkflows/local/utils_nfcore_plumb_pipeline'
include { PIPELINE_COMPLETION     } from './subworkflows/local/utils_nfcore_plumb_pipeline'
// Include modules
include { PRINT_STRATEGY } from './modules/local/messages/main.nf'
include {PROCESS_INPUT } from './modules/local/prep_dock/main.nf'
include {DOWNLOAD_BINDINGDB } from './modules/local/import/main.nf'
include {PROCESS_BINDINGDB } from './modules/local/import/main.nf'
include {PROCESS_BINDINGDB_W_CH } from './modules/local/import/main.nf'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    NAMED WORKFLOWS FOR PIPELINE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// WORKFLOW: Run main analysis pipeline depending on type of input
//
workflow NFCORE_PLUMB {

    take:
    samplesheet // channel: samplesheet read in from --input

    main:

    //
    // WORKFLOW: Run pipeline
    //
    PLUMB (
        samplesheet
    )
}

/*
~~~~~~~~~~~~~~~~
ABC customizations from tutorial
~~~~~~~~~~~~~~~~
*/
/*
 * Use echo to print 'Hello World!' to standard out
 */





/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow {
    // dock_ch = Channel.of(params.docking)
    // dist_ch = Channel.of(params.pocket_dist)
    // printStrategy(dock_ch, dist_ch)
    // DOWNLOAD_BINDINGDB()
    PRINT_STRATEGY(params.docking, params.pocket_dist)
    input_dir = file(projectDir).resolve("raw_data/binding_db") 
    PROCESS_BINDINGDB(input_dir)
    // Define an input channel with a clear name
    // Channel.fromPath("${projectDir}/raw_data/binding_db/*3D.sdf")  // Creates a channel from all matching SDF files
    //     | map { file(it) }  // Converts each path string to a Nextflow file object
    //     | PROCESS_BINDINGDB_W_CH  // Sends each file as input to the process


    // PROCESS_INPUT()

    // main:
    //
    // SUBWORKFLOW: Run initialisation tasks
    //
    // PIPELINE_INITIALISATION (
    //     params.version,
    //     params.validate_params,
    //     params.monochrome_logs,
    //     args,
    //     params.outdir,
    //     params.input
    // )

    // //
    // // WORKFLOW: Run main workflow
    // //
    // NFCORE_PLUMB (
    //     PIPELINE_INITIALISATION.out.samplesheet
    // )
    // //
    // // SUBWORKFLOW: Run completion tasks
    // //
    // PIPELINE_COMPLETION (
    //     params.email,
    //     params.email_on_fail,
    //     params.plaintext_email,
    //     params.outdir,
    //     params.monochrome_logs,
    //     params.hook_url,
    // )
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
