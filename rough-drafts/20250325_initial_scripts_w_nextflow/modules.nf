process PROCESS_BINDINGDB {
    conda "${params.asap2025}"
    tag "process_bindingdb"
    clusterOptions '--partition cpushort'

    output:
    path("*.json"), emit: input_json
    path("*.sdf"), emit: input_sdf

    script:
    """
    python "${params.scripts}/process_bindingdb.py" "${params.bindingDB}"
    """
}
