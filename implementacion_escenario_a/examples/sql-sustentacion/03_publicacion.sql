SELECT active.generation AS generation_id,
       json_extract(generations.receipt, '$.collection') AS coleccion_qdrant,
       json_extract(generations.receipt, '$.key.perfil') AS perfil,
       json_extract(generations.receipt, '$.key.revision_gobierno') AS revision_gobierno,
       json_extract(generations.receipt, '$.key.bundle_fingerprint') AS bundle_fingerprint
FROM generations
JOIN active ON generations.id = active.generation;
