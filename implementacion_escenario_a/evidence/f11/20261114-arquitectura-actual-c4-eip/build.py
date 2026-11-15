"""Documento actualizado del proyecto completo en cuatro páginas con C4 y EIP."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
# Reutiliza únicamente los estilos y ayudantes de autoría, sin ejecutar el informe anterior.
prefix=(BASE.parent/'f9_2_documento/build.py').read_text(encoding='utf-8').split(
    "doc.add_heading('Funcionamiento del arnés F9.2',0)")[0]
prefix=prefix.replace('Arquitectura_C4_EIP_y_Funcionamiento_Arnes_F9_2.docx',
                      'Arquitectura_Actual_PetroAndes_C4_EIP_F9_2.docx')
prefix=prefix.replace('Arnés F9.2  ·  14 noviembre 2026', 'Arquitectura actual  ·  F9.2  ·  14 noviembre 2026')
exec(compile(prefix,'estilos_documento','exec'))
doc.core_properties.title='Arquitectura actual y funcionamiento de PetroAndes'
doc.core_properties.subject='Sistema documental del Escenario A con C4, EIP y arnés F9.2'

doc.add_heading('Arquitectura actual de PetroAndes',0)
p('Funcionamiento del proyecto con vistas C4 e integración EIP','Subtitle')
p('Escenario A de ARTI 4212  ·  Estado documentado al 14 de noviembre de 2026')
p('PetroAndes convierte PDF técnicos en evidencia consultable con permisos documentales, '
  'extractos literales y citas verificables. Su implementación local integra Python, SQLite, '
  'Qdrant, E5, BM25 y MCP. La actualización F9.2 incorpora señales de contenido y propiedades '
  'del PDF, auditoría por llamada y un cliente restringido para probar documentos envenenados. '
  'Este informe describe el sistema completo, desde la fuente hasta la respuesta y su validación.')
figure('c4_contexto','Figura 1  C4 nivel 1  Contexto del sistema y responsabilidades externas',
        'El consultante usa Inspector o VS Code para consultar PetroAndes. El revisor registra '
        'decisiones por una ruta administrativa distinta. El sistema devuelve evidencia o abstención.')
h('Qué hace el sistema y quién decide el acceso')
p('El consultante formula una pregunta o solicita una sección; el sistema devuelve datos '
  'documentales autorizados. El revisor determina, por evidencia y hash, qué puede usarse para '
  'cada grupo, ámbito, finalidad y período. La similitud del texto no otorga permisos. El corpus '
  'y las respuestas de herramientas se tratan como datos no confiables, incluso cuando contienen órdenes.')
table(('Ejemplo de presentación','Comportamiento documentado'),[
    ('Presión de descarga de P-101','Diseño 1.180 psi y alarma 1.240 psi, con cita a la ficha v2.'),
    ('Incertidumbre de medición','Máximo 0,3 %, con cita al artículo 2 de RES-CREG-0043-2024.'),
    ('Anexo de COM-PRV-0134','Búsqueda con abstención y descarte trazado; la lectura literal autorizada conserva el documento para auditoría.')
],(2.35,4.75))
p('La presentación usa un único servidor lógico petroandes en Inspector y VS Code/Copilot. '
  'La demo reproduce la revisión 15 aprobada con reloj histórico del 8 de noviembre de 2026: '
  '14 documentos autorizados y 68 fragmentos, a partir de 19 PDF y 92 fragmentos preparados. '
  'Cada cliente inicia un proceso con catálogo e índice privados; esto evita propietarios '
  'simultáneos de una carpeta Qdrant. El servicio entrega evidencia del corpus; no consulta OT en tiempo real.')

page('Construcción y persistencia del sistema')
figure('c4_contenedores','Figura 2  C4 nivel 2  Aplicaciones y almacenes con sus interacciones principales',
        'Las fuentes y E5 alimentan la CLI. El gobierno SQLite autoriza el servidor. Las proyecciones '
        'Qdrant y SQLite son derivadas. Los clientes acceden por stdio y se guardan recibos locales.')
lead('Ingesta y preparación.', 'pypdf extrae texto, tablas, secciones y páginas. Markdown contrasta '
     'la extracción; los PDF siguen siendo la fuente. La partición estructural conserva condiciones, '
     'unidades, filas, orden y parentesco. Cada fragmento incorpora identidad, hash y procedencia. '
     'F9.2 añade las señales textuales y visuales sin modificar el original. Una extracción dudosa '
     'requiere revisión antes de publicarse.')
lead('Representación y publicación.', 'El modelo intfloat/multilingual-e5-small produce vectores '
     'normalizados de 384 dimensiones, con prefijos query: y passage:. El bundle fijado es '
     'e5small-es-1.0.0 y admite hasta 448 tokens de entrada. El publicador selecciona documentos '
     'elegibles y prepara Qdrant local, proyecciones SQLite, términos BM25 y manifiestos con huellas. '
     'Verifica la generación completa y la revisión de gobierno antes de activarla.')
lead('Gobierno y cambios F10.', 'SQLite conserva documentos, decisiones y revisiones. Las decisiones '
     'y sus eventos quedan registrados conjuntamente en un outbox; la propagación confirma eventos '
     'tras publicar y trata repeticiones de forma idempotente. Un PDF modificado exige revisar el nuevo '
     'hash. Una revocación afecta la consulta aunque permanezca un vector antiguo. Reindexar o '
     'revertir derivados no restaura una autorización revocada.')
p('Un contenedor C4 representa una aplicación o un almacén, no un contenedor Docker. '
  'La imagen del proyecto soporta el perfil dev; los módulos se agrupan por responsabilidad '
  'y comparten un núcleo Python. Qdrant se usa en modo local embebido, no como un servicio HTTP '
  'independiente. La demo reutiliza este núcleo para preparar sus propios derivados temporales.')

page('Consulta gobernada y controles del arnés F9.2')
figure('c4_componentes','Figura 3  C4 nivel 3  Componentes del servidor durante una consulta',
        'MCP valida contratos. El recuperador invoca elegibilidad y composición. F6 consulta señales '
        'de seguridad. La auditoría registra inicio y cierre antes de entregar la respuesta.')
lead('Recuperación y respuesta.', 'buscar_documentos recibe consulta, top_k entre 1 y 10 y filtros '
     'opcionales de tipo, activo o tramo. El servicio calcula primero IDs elegibles: Qdrant filtra '
     'la rama densa y BM25 puntúa solo ese conjunto. Los códigos completos y las versiones ayudan '
     'a precisar coincidencias; RRF combina posiciones. Se revalida el gobierno antes de devolver '
     'evidencia. F6 exige intención admitida, contexto suficiente y citas literales; si no puede '
     'sostener la respuesta, se abstiene.')
p('obtener_fragmento recibe doc_id, version_documental y section_id; admite hash o parte para '
  'precisar la referencia. Usa la misma elegibilidad, conserva partes ordenadas y marca el '
  'contenido como no confiable. Ninguna herramienta permite elegir grupos, uso, perfil ni reloj. '
  'Los errores de esquema se distinguen de una denegación documental o un índice no disponible.')
table(('Mejora F9.2','Control implementado'),[
    ('Detector de contenido y PDF','Normaliza Unicode, examina sustitución de instrucciones, rol, ocultación, envío externo y variantes URL/base64. PyMuPDF detecta texto invisible, microscópico, fuera de página o sin contraste. F6 descarta unidades señaladas; no elimina el PDF ni cambia permisos.'),
    ('Auditoría por llamada','Cada tools/call crea un recibo iniciado y lo cierra de forma durable antes de responder. Incluye correlation_id, huellas, revisión, generación, señales y chunks descartados, sin consulta ni texto. Si no puede escribir, falla sin entregar evidencia.'),
    ('Cliente y sandbox','El cliente dedicado congela hasta diez lecturas antes de recibir documentos y valida contrato, literalidad y citas. No tiene LLM ni intérprete de acciones. f9-sandbox limita red, escritura y recursos con UID 10001, fuente y pesos RO, cap_drop ALL y no-new-privileges.')
],(1.5,5.6))
p('El anexo original también provoca abstención por la regla de intención no admitida; una '
  'abstención aislada no identifica su causa. El arnés comprueba recuperación y descarte del chunk '
  'objetivo, exposición literal y ausencia de acciones indebidas. Copilot conserva capacidades '
  'propias; la contención verificada del cliente dedicado no se extiende automáticamente al IDE.')

page('Integración EIP y evidencia del funcionamiento')
figure('eip_integracion','Figura 4  Integración EIP de preparación y consulta del sistema',
        'La ingesta adapta PDF, divide secciones, enriquece fragmentos y almacena derivados. '
        'MCP adapta consultas, filtra elegibilidad, agrega rankings y aplica filtro y suficiencia F6.')
lead('Correspondencia con EIP.', 'Channel Adapter representa la adaptación de PDF y MCP; Splitter '
     'corresponde a la división estructural; Content Enricher incorpora contexto, procedencia y '
     'señales; Message Store representa derivados persistidos. Aggregator combina rankings con '
     'RRF y Message Filter modela elegibilidad y descarte. Request Reply describe las consultas '
     'síncronas; Correlation Identifier vincula respuesta y recibo. Son correspondencias funcionales: '
     'no se incorporan broker ni colas de consulta persistentes.')
lead('Flujo del ataque y utilidad.', 'Al buscar el anexo envenenado de COM-PRV-0134 se conserva '
     'su recuperación y se evidencia el descarte en la traza F6; la respuesta se abstiene. '
     'La obtención directa autorizada permite inspección literal sin ejecutar órdenes. '
     'La pregunta legítima al mismo documento responde firmware 7.4, condiciones y citas. '
     'El cliente restringido no transforma ese texto en correo, comandos ni nuevas consultas.')
lead('Validación conservada.', 'Docker dev aprobó 255 pruebas y cuatro fases: F9 original con '
     '19 comprobaciones, fronteras MCP con 17, doce PDF nuevos con siete adversariales detectados '
     'y cinco benignos sin falsos positivos en ese conjunto, y 23 casos sintéticos F9.1. '
     'El flujo PDF produjo 24 llamadas y 26 recibos completos. Se verificaron aislamiento, '
     'receptor de red positivo antes y después, limpieza e integridad de 379 fuentes. '
     'No se ejecutó la reserva formal.')
p('F8 usa laya multilingüe para evaluar soporte por afirmación y pertinencia por fragmento; '
  'la evaluación formal congelada sigue pendiente. F11 reúne código, guías y evidencia '
  'para la entrega, conservando paquetes anteriores.')
lead('Operación y límites.', 'Los recibos habituales están en reports/portable/mcp-audit/ con '
     'nombre <correlation_id>.json. El ensayo integral escribe summary.json y los resultados '
     'de sus cuatro fases en la carpeta asignada. El detector es heurístico, sin OCR ni garantía '
     'universal; Copilot y un LLM real permanecen sin evaluación adversarial. Los recibos locales '
     'no son un almacén inviolable. Esta actualización documental usa evidencia existente y no '
     'repite los ataques ni la reserva.')
para=p('Fuentes del proyecto: ','Caption')
link(para,'Arquitectura F9.2','../../implementacion_escenario_a/docs/adr-0015-arnes-f9-2.md'); para.add_run('  ·  ')
link(para,'Guía de validación','../../implementacion_escenario_a/docs/validacion-dev-f9-2.md'); para.add_run('  ·  ')
link(para,'Evidencia Docker','../../implementacion_escenario_a/evidence/f9/20261114-arnes-contenido/README.md')
para.add_run('  ·  ')
link(para,'Evaluación F8','../../implementacion_escenario_a/docs/validacion-dev-f8.md')
para=p('Notación: ','Caption')
link(para,'C4 de Simon Brown','https://c4model.com/'); para.add_run('  ·  ')
link(para,'Enterprise Integration Patterns','https://www.enterpriseintegrationpatterns.com/patterns/messaging/')
para.add_run('. C4 y EIP: CC BY 4.0. Iconos EIP de Gregor Hohpe y Bobby Woolf; diagramas propios y adaptaciones atribuidas.')
OUT.parent.mkdir(parents=True,exist_ok=True)
doc.save(OUT)
print(OUT)
