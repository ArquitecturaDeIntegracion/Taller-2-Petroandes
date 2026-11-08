# F5. Recuperación híbrida gobernada

La interfaz Python es `petroandes.retrieve.Retriever`. El operador puede probar
`buscar`, `obtener` y `expandir` con `tools/f5.py`. Las entradas de búsqueda y
obtención usan los contratos F1. El proceso selecciona el despliegue y toma su
contexto de `config/f4-context.json`. La guía incluye comandos y salidas esperadas.
[Validación en Docker](validacion-dev-hasta-f5.md).

## Elegibilidad y consistencia

El catálogo externo determina elegibilidad por revisión, identidad documental y
hash. Si no hay documentos elegibles, se omiten la apertura de Qdrant y las dos
ramas. Si hay elegibles, se valida el recibo F4, las proyecciones y el bundle bajo
un único propietario Qdrant. El índice con revisión distinta bloquea la consulta
hasta una publicación coherente. Si expira un permiso en la misma revisión, se
excluyen sus IDs del conjunto consultable aunque el punto y los términos sigan
almacenados. La apertura estricta administrativa de F4 conserva su comportamiento.

Los filtros de tipo, tag de activo y tramo reducen ese conjunto antes de puntuar.
Los tramos se comparan por los valores observados en las tablas F3, con
normalización de mayúsculas y separadores. Qdrant recibe los IDs permitidos,
generación, revisión y huella del bundle en la propia consulta. SQLite une los
términos con los IDs permitidos antes de construir BM25.

La revisión y el conjunto autorizado se comprueban de nuevo al terminar, incluso
si no hubo resultados. Ante un cambio se descartan los candidatos de la salida
y de su traza. Se optó por abstenerse ante una carrera en vez de repetir la consulta.

## Ranking y acceso directo

La tokenización `bm25-codes-es-1.0.0` usa palabras Unicode en minúscula y preserva
separadores internos `-`, `.` y `/`. `codes-es-1.0.0` identifica códigos completos,
respeta años y versiones explícitas (`v1`, `versión 1`) y compara con identidad
documental o tags de activo observados. La búsqueda interpreta `v1` como el
valor de versión `1` registrado en el PDF. El alias `P101` corresponde a `P-101`.
Un código aislado, con versión opcional, restringe las dos ramas a coincidencias
exactas autorizadas. En texto libre, la coincidencia exacta tiene precedencia dentro
del ranking léxico. Los códigos sustituidos se tratan como identidades distintas.

Se toman hasta 10 candidatos por rama y se fusionan por RRF con constante 60.
Los empates de cada rama usan el ID de fragmento. En RRF, el desempate favorece
la coincidencia exacta y luego el ID. Las trazas registran ramas, seleccionados,
parámetros, tiempos, generación, revisión y `correlation_id`. El contrato de
búsqueda F5 devuelve candidatos con citas para composición en F6.

La obtención respeta código, versión nullable, sección y parte o SHA-256
opcional. Si hay más de una huella elegible para código y versión, el selector
exige el SHA-256 antes de elegir sección. El catálogo F2 admite un hash activo
por código y versión, de modo que el caso de emisiones simultáneas se comprobó
en el selector con dos referencias autorizadas. La expansión usa partes
publicadas del mismo padre y secciones de condiciones enlazadas por F3, bajo
la misma identidad y huella. Cada parte lleva cita y marca de contenido no confiable.

## Alcance de la verificación

Se compararon las ramas en un laboratorio sintético y en un ensayo histórico
aislado que usa los permisos simulados registrados y vuelve a ingerir los PDF.
La comparación sobre los casos de ajuste propuestos queda pendiente de la
revisión humana de F1. La prueba de revocación conserva las proyecciones antiguas
y examina sus datos físicos desde la prueba, fuera de las rutas del servicio.
