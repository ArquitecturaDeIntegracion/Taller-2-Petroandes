SELECT chunk_id,
       json_extract(payload, '$.fragment.doc_id') AS documento,
       json_extract(payload, '$.fragment.section_id') AS seccion,
       json_extract(payload, '$.fragment.pdf_sha256') AS pdf_sha256,
       json_extract(payload, '$.fragment.pagina_inicio') AS pagina_inicio,
       json_extract(payload, '$.fragment.pagina_fin') AS pagina_fin,
       json_extract(payload, '$.fragment.contenido_no_confiable') AS contenido_no_confiable,
       json_extract(payload, '$.metadata.seguridad.trust_level') AS confianza,
       json_extract(payload, '$.metadata.seguridad.security_flags') AS marcas_seguridad,
       json_extract(payload, '$.fragment.texto') AS texto_integro
FROM fragments
WHERE json_extract(payload, '$.fragment.doc_id') = 'COM-PRV-0134'
  AND json_extract(payload, '$.fragment.section_id') = 'anexo-notas-de-integracion';
