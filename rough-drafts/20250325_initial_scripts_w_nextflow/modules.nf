process PROCESS_BINDINGDB {
    publishDir "${params.output}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "process_bindingdb"
    clusterOptions '--partition cpushort'

    output:
    path("*.json"), emit: input_json
    path("*.sdf"), emit: input_sdf

    script:
    """
    python "${params.scripts}/process_bindingdb.py" --input-dir "${params.bindingDB}"
    """
}
process DOWNLOAD_PDB {
    conda "${params.asap}"
    tag "download_pdb"
    clusterOptions '--partition cpushort'

    output:
    path("*.cif"), emit: input_cif

    script:
    """
    python "${params.scripts}/download_pdb.py"
    """
