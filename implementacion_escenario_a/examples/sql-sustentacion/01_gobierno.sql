SELECT perfil,
       schema_version,
       revision AS revision_gobierno,
       (SELECT COUNT(*) FROM documents) AS documentos,
       (SELECT COUNT(*) FROM decisions) AS decisiones,
       (SELECT COUNT(*) FROM events) AS eventos
FROM metadata;
