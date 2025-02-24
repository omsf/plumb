#!/usr/bin/env nextflow

process PRINT_STRATEGY {

    publishDir 'results', mode: 'copy'

    input: 
        val dock_alg
        val pocket_threshold
    
    output:
        path 'strategy.txt'

    script:
    """
    echo 'Docking Algorithm: $dock_alg' > strategy.txt
    echo 'Threshold: $pocket_threshold Angstrom' >> strategy.txt
    """
}