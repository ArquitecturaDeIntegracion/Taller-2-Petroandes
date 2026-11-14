SELECT json_extract(payload, '$.fragment.doc_id') AS documento,
       json_extract(payload, '$.fragment.version_documental') AS version,
       COUNT(*) AS fragmentos_documento,
       SUM(COUNT(*)) OVER () AS total_fragmentos_publicados,
       COUNT(*) OVER () AS documentos_publicados
FROM fragments
GROUP BY json_extract(payload, '$.fragment.doc_id'),
         json_extract(payload, '$.fragment.version_documental')
ORDER BY documento, version;
