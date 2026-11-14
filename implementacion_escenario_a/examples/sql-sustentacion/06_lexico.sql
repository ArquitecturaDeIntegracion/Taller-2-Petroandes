SELECT COUNT(*) AS fragmentos_lexicos,
       MIN(json_array_length(payload)) AS minimo_tokens_por_fragmento,
       MAX(json_array_length(payload)) AS maximo_tokens_por_fragmento
FROM fragments;
