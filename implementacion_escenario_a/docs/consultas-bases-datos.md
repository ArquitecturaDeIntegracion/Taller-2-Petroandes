# Consultas directas de bases de datos para la sustentación

Ejecutar en PowerShell desde `implementacion_escenario_a`. Docker Desktop
debe usar contenedores Linux. Enviar cada comando completo por separado.
No es necesario escribir JSON ni instalar sqlite3 en Windows.

## Qué se consulta

La herramienta prepara una copia aislada de la demostración: snapshot
aprobado de revisión 15, reloj histórico del 8 de noviembre de 2026,
19 documentos inventariados y 14 documentos elegibles que publican 68
fragmentos. Reconstruye desde PDF; no abre la base privada del MCP activo.
No añade otro servidor de presentación ni cambia sus permisos.

Qdrant funciona como biblioteca local mediante `QdrantClient(path=...)`;
este proyecto no expone una API Qdrant en el puerto 6333. Solo un proceso
puede ser propietario de cada directorio Qdrant local. La copia aislada evita
competir con Inspector o Copilot por ese directorio.

SQLite cumple varias funciones separadas:

| Base de la herramienta | Función |
| --- | --- |
| gobierno | Documentos, decisiones académicas, observaciones y eventos. |
| publicaciones | Puntero a la generación activa y recibo de su colección Qdrant. |
| fragmentos | Texto, citas, padres y metadatos de la generación publicada. |
| lexico | Tokens por fragmento empleados para construir BM25. |

Las consultas `sql` abren las bases en modo de solo lectura. Las consultas
directas son inspección técnica: no aplican por sí mismas el contexto de
autorización de MCP ni el descarte del compositor F6. Un dato presente en
una base no equivale a permiso de lectura ni a una recomendación operativa.

## Preparar los datos una sola vez

```powershell
docker compose --profile dev build dev
$datos = 'reports/portable/bd-sustentacion-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
docker compose --profile dev run --rm -T dev tools/db_demo.py preparar --output-dir $datos
```

Conservar `$datos` en esa consola y usar siempre una carpeta nueva al preparar
otra copia. Los modelos E5 deben estar preparados en `model-cache`; si faltan,
seguir la [preparación de E5](validacion-dev-f9-1.md). La preparación puede
tardar varios minutos. No copiar un índice Qdrant mientras otro proceso escribe.

## Consultas SQL de evidencia

Los archivos contienen una consulta SELECT por ejecución. Cada comando
envía el archivo SQL al motor SQLite; no es una consulta al modelo de IA.

1. Mostrar revisión e inventario del gobierno documental:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py sql --workspace $datos --base gobierno --sql examples/sql-sustentacion/01_gobierno.sql
```

Esperado: perfil laboratorio, esquema 1, revisión 15, 19 documentos,
14 decisiones y 15 eventos. El número de eventos es historial del snapshot,
no un indicador de acciones que deban ejecutarse durante esta demostración.

2. Mostrar el permiso académico de la comunicación envenenada:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py sql --workspace $datos --base gobierno --sql examples/sql-sustentacion/02_decisiones.sql
```

Esperado: COM-PRV-0134, sin versión documental, decisión 12, certificado
simulado, grupo LAB_REVISION y contenido no confiable. Los usos incluyen
evidencia_historica e inspeccion_no_confiable. El fin exclusivo es el
1 de diciembre de 2026 a las 00:00 en zona -05:00. La revisión general
sigue siendo 15: la revisión 12 identifica esa decisión individual.

3. Mostrar qué generación y colección están activas:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py sql --workspace $datos --base publicaciones --sql examples/sql-sustentacion/03_publicacion.sql
```

Esperado: una generación de laboratorio en revisión 15, su colección
Qdrant y huella del bundle. El nombre de colección es variable; no copiar
el nombre de una corrida anterior como si fuera una constante.

4. Mostrar los fragmentos publicados por documento:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py sql --workspace $datos --base fragmentos --sql examples/sql-sustentacion/04_fragmentos.sql
```

Esperado: 14 filas de documentos/versiones y total de 68 fragmentos.
Los 19 documentos del inventario y los 14 publicados representan conjuntos
distintos: la publicación se limita a la elegibilidad del contexto histórico.

5. Mostrar el anexo íntegro y sus marcas de seguridad:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py sql --workspace $datos --base fragmentos --sql examples/sql-sustentacion/05_anexo.sql
```

Esperado: sección anexo-notas-de-integracion de COM-PRV-0134, chunk_id,
SHA-256 del PDF, páginas, texto íntegro, contenido_no_confiable igual a 1,
confianza untrusted y marca instrucciones_dirigidas_al_procesador.
Mostrar el texto sirve para acreditar que el ataque se conserva como dato;
su contenido no autoriza ejecutar las instrucciones que aparecen allí.

6. Mostrar la proyección léxica que alimenta BM25:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py sql --workspace $datos --base lexico --sql examples/sql-sustentacion/06_lexico.sql
```

Esperado: 68 fragmentos léxicos. Los tokens se almacenan como arrays JSON;
los puntajes BM25 se calculan al consultar los fragmentos elegibles.
La tabla no es un índice SQLite FTS ni almacena puntajes permanentes.

También puedes escribir una consulta de lectura para explorar las tablas:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py sql --workspace $datos --base gobierno --query "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
```

Esperado: metadata, documents, document_history, observations, relations,
decisions, conflicts y events. La herramienta rechaza escrituras y ATTACH.

## Consultar Qdrant directamente

Mostrar colección, cantidad y configuración vectorial:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py qdrant --workspace $datos
```

Esperado: colección activa con 68 puntos, dimensión 384 y distancia COSINE.

Mostrar el punto del anexo, sus metadatos y vector:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py qdrant --workspace $datos --doc-id COM-PRV-0134 --section-id anexo-notas-de-integracion --vector
```

Esperado: el mismo chunk_id y SHA-256 del PDF mostrados en la consulta SQL 5,
contenido_no_confiable igual a true y governance_revision igual a 15.
La salida muestra la dimensión 384 y las primeras ocho coordenadas del vector.
Las marcas security_flags se muestran en
la proyección SQLite; no son un campo del payload Qdrant de este proyecto.

Probar una búsqueda densa con E5 y Qdrant:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py qdrant --workspace $datos --consulta "P-101 presión de diseño" --top-k 3
```

Se solicitan hasta tres coincidencias, con puntajes de similitud y referencias
documentales. Conservar el resultado observado; no atribuir un ranking fijo
sin comprobar esa corrida. Esta operación no combina BM25 ni produce una
respuesta F6 con citas por afirmación.

## Cómo presentar la prueba del documento envenenado

Para guardar la salida de una consulta además de verla en la consola:

```powershell
docker compose --profile dev run --rm -T dev tools/db_demo.py qdrant --workspace $datos --doc-id COM-PRV-0134 --section-id anexo-notas-de-integracion --vector | Tee-Object -FilePath (Join-Path $datos 'evidencia-anexo-qdrant.txt')
```

`db-demo.json`, en la carpeta `$datos`, identifica la colección, la generación
y las rutas relativas de los archivos SQLite y del directorio Qdrant de la copia.

Mostrar el permiso académico en SQL 2, el texto no confiable en SQL 5 y
el mismo identificador en Qdrant. Después mostrar la traza F9 donde ese
fragmento se recuperó y quedó en descartados_seguridad al componer.
[Evidencia del arnés](../evidence/f9/20261113-arnes-ampliado/README.md).
Estas consultas directas no ejecutan el arnés ni actualizan su reporte.

No usar un GROUP BY sobre observations como clasificación actual: conserva
las observaciones iniciales. Las 14 decisiones del snapshot son certificados
simulados para LAB_REVISION; la elegibilidad efectiva también depende de
hash, uso, ámbito y período. Se usa un reloj histórico explícito para esta
demostración, no una declaración de vigencia real.

Referencias de API: [cliente Qdrant local](https://github.com/qdrant/qdrant-client#local-mode)
y [SQLite de solo lectura](https://docs.python.org/3.12/library/sqlite3.html#how-to-work-with-sqlite-uris).

## Copia ya validada en este equipo

Puedes reutilizar los datos de la corrida comprobada sin volver a reconstruir:

```powershell
$datos = 'reports/portable/db-sustentacion-20261113-validacion/datos'
```

La corrida aprobó seis consultas SQL, dos Qdrant y dos denegaciones SQL.
[Recibos y resultados observados](../evidence/db/20261113-sustentacion/README.md).
