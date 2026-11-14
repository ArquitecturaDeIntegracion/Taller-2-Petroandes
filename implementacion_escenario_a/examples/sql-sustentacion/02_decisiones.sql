SELECT revision AS revision_decision,
       json_extract(payload, '$.decision.doc_id') AS documento,
       json_extract(payload, '$.decision.version_documental') AS version,
       json_extract(payload, '$.decision.estado') AS estado,
       json_extract(payload, '$.decision.pdf_sha256') AS pdf_sha256,
       json_extract(payload, '$.decision.usos') AS usos,
       json_extract(payload, '$.decision.grupos') AS grupos,
       json_extract(payload, '$.decision.simulacion_academica') AS simulacion_academica,
       json_extract(payload, '$.decision.effective_to') AS fin_exclusivo,
       json_extract(payload, '$.contenido_no_confiable') AS contenido_no_confiable
FROM decisions
WHERE json_extract(payload, '$.decision.doc_id') = 'COM-PRV-0134'
ORDER BY revision DESC;
