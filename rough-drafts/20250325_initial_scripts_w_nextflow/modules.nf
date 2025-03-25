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
    python "${params.scripts}/process_bindingdb.py" --input-dir "${params.bindingDB}"
    """
}
process DOWNLOAD_PDB {
    publishDir "${params.output}", mode: 'copy', overwrite: true
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
    python "${params.scripts}/download_pdb.py" --input-json "${input_json}"
    """
}
process PREP_CIF {
    publishDir "${params.output}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "${uuid}"
    clusterOptions '--partition cpushort'

    input:
    tuple val(uuid), path(input_cif, stageAs:"input.cif")
    tuple val(uuid), path(input_json, stageAs:"input.json")


    script:
    """
    python "${params.scripts}/prep_cif.py" --input-json "${input_json}" --input-cif "${input_cif}" --fasta-sequence "${params.fasta}"
    """

}
