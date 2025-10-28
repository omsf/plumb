process PROCESS_BINDINGDB {
    publishDir "${params.output}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "process_bindingdb"
    clusterOptions '--partition cpushort'

    output:
    path("*.json"), emit: input_json
    path("*.sdf"), emit: input_sdf
    path("*.csv"), emit: input_csv
    path("*.txt"), emit: input_txt

    script:
    """
    plumbline process-bindingdb \
    	      --input-directory "${params.bindingDB}" \
	      --output-directory "./"
    """
}
process DOWNLOAD_PDB {
    publishDir "${params.output}/${uuid}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(input_json, stageAs:"input.json")

    output:
    tuple val(uuid), path("*.cif"), emit: input_cif
    tuple val(uuid), path("*.json"), emit: record_json

    script:
    """
    plumbline download-pdb \
              --input-file "${input_json}"
    """
}
process PREP_CIF {
    publishDir "${params.output}/${uuid}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(input_cif, stageAs:"input.cif"), path(input_json, stageAs:"input.json")

    output:
    tuple val(uuid), path("*spruced_complex.pdb"), emit: prepped_pdb
    tuple val(uuid), path("*ligand.sdf"), emit: ligand_sdf
    tuple val(uuid), path("*.json"), emit: record_json



    script:
    """
    plumbline prep-cif \
              --input-json "${input_json}" \
              --input-cif "${input_cif}" \
              --fasta-sequence "${params.fasta}" \
              --output-directory "./"
    """
}
process PREP_FOR_DOCKING {
    publishDir "${params.output}/${uuid}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(prepped_pdb, stageAs: "prepped_complex.pdb")

    output:
    tuple val(uuid), path("*/*ligand.sdf"), emit: ligand_sdf
    tuple val(uuid), path("*/*spruced_complex.pdb"), emit: prepped_pdb
    tuple val(uuid), path("*/*.json"), emit: json_schema
    tuple val(uuid), path("*/*.oedu"), emit: design_unit

    script:
    """
    asap-cli protein-prep \
             --target SARS-CoV-2-Mpro \
             --pdb-file "${prepped_pdb}" \
             --output-dir "./"
    """
}
process ASSESS_PREPPED_PROTEIN {
    publishDir "${params.output}/${uuid}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(design_unit, stageAs: "design_unit.oedu")

    output:
    tuple val(uuid), path("*.json"), emit: report_json

    script:
    """
    plumbline assess-prepped-protein \
              --input-file "${design_unit}" \
              --output-directory "./"
    """
}
process GENERATE_CONSTRAINED_LIGAND_POSES {
    publishDir "${params.output}/${uuid}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(prepped_complex_json_schema, stageAs: "json_schema.json")

    output:
    tuple val(uuid), path("*.sdf"), emit: posed_ligands

    script:
    """
    plumbline generate-constrained-ligand-poses \
              --input-sdf "${params.congenericSeries}" \
              --prepped-schema "${prepped_complex_json_schema}" \
              --output-directory "./"
    """

}
process MAKE_FEC_INPUTS {
    publishDir "${params.output}/${uuid}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(posed_ligands, stageAs: "posed_ligands.sdf"), path(prepped_complex, stageAs: "prepped_complex.pdb")

    output:
    tuple val(uuid), path("*/*.graphml"), emit: network_graph
    tuple val(uuid), path("*/*.json"), emit: network_json

    script:
    """
    asap-cli alchemy create fecs-workflow.json

    asap-cli alchemy plan \
             -f fecs-workflow.json \
             --name ${uuid}_plumb_alchemiscale_network \
             --receptor "${prepped_complex}" \
             --ligands "${posed_ligands}" \
    """
}
process VISUALIZE_NETWORK {
    publishDir "${params.output}/${uuid}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(network_graph, stageAs: "network.graphml")

    output:
    tuple val(uuid), path("*.png"), emit: network_png

    script:
    """
    plumbline visualize-network \
              --network-graphml "${network_graph}" \
              --output-directory "./"
    """
}