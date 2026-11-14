"""Suite F9.1 aislada: evidencia reproducible sin conectar al sistema productivo."""
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from petroandes.extract.output import write_json, write_jsonl
from .cases import matriz
from .client import ClienteForzado
from .dispatcher import Despachador, DobleLectura
from .grading import evaluar, metricas
from .models import Estado, plan_inicial


def ejecutar_caso(caso, ejecucion):
    plan = plan_inicial(caso.identidad)
    fuente = DobleLectura(caso.corromper_recurso)
    despachador = Despachador(plan, fuente)
    cliente = ClienteForzado(caso, plan, f'{ejecucion}/{caso.id}')
    eventos, recibidos, propuestas, decisiones = [], (), [], []
    error = None

    def registrar(estado, **datos):
        eventos.append({'caso': caso.id, 'sesion': cliente.sesion, 'estado': estado.value,
                        'plan_sha256': cliente.plan_sha256, 'alcance': 'frontera_consumidor', **datos})

    registrar(Estado.PREPARADO, identidad=plan.identidad, uso=plan.uso)
    try:
        total = len(caso.propuestas) + int(caso.borrador is not None)
        for turno in range(1, total + 1):
            anteriores = len(recibidos)
            recibidos = cliente.recibir(turno)
            for recibo in recibidos[anteriores:]:
                registrar(Estado.EXPUESTO, recibo=recibo)
            propuesta_actual = cliente.proponer(turno)
            propuestas.extend(propuesta_actual)
            tipo, propuesta = propuesta_actual[0]
            registrar(Estado.PROPUESTO, turno=turno, tipo=tipo, propuesta=propuesta,
                      origen='documento_no_confiable', modo='cliente_forzado_sin_llm')
            decision = (despachador.despachar(propuesta) if tipo == 'herramienta'
                        else despachador.validar_borrador(propuesta))
            decisiones.append(decision)
            registrar(Estado.DECIDIDO, turno=turno, resultado=decision,
                      lecturas_del_doble=list(fuente.llamadas))
    except Exception as fallo:  # Una falla de infraestructura o del evaluador no acredita contención.
        error = f'{type(fallo).__name__}: {fallo}'
    resultado = evaluar(caso, recibidos, propuestas, decisiones, fuente.llamadas, error, cliente.sesion)
    estado = Estado.INCONCLUSO if resultado['status'] == 'inconcluso' else Estado.EVALUADO
    registrar(estado, resultado=resultado)
    return resultado, eventos


def run_suite(destination: Path) -> dict:
    """Crea un directorio de evidencia nuevo; rechaza sobrescribir ejecuciones anteriores."""
    destino = Path(destination)
    destino.mkdir(parents=True, exist_ok=False)
    ejecucion = str(uuid4())
    casos = matriz()
    archivos_casos = write_jsonl(destino, 'casos', [caso.model_dump(mode='json') for caso in casos])
    resultados, eventos = [], []
    for caso in casos:
        resultado, traza = ejecutar_caso(caso, ejecucion)
        resultados.append(resultado)
        eventos.extend(traza)
    benignos = [fila for fila in resultados if fila['objetivo'] == 'benigno']
    estado = 'passed' if all(fila['status'] == 'passed' for fila in resultados) else 'failed'
    resumen = {'schema_version': 'f9.1-1', 'status': estado, 'ejecucion': ejecucion,
               'fecha_utc': datetime.now(timezone.utc).isoformat(), 'alcance': 'frontera_consumidor',
               'tipo_casos': 'fixtures_sinteticos_publicos_distintos_de_A_R',
               'cliente': 'adversarial_determinista_forzado_sin_detector_semantico',
               'llm': {'estado': 'no_evaluado', 'motivo': 'No se invoca modelo ni API externa'},
               'rag_real': 'no_evaluado_por_esta_suite', 'casos': len(casos),
               'passed': sum(fila['status'] == 'passed' for fila in resultados),
               'failed': sum(fila['status'] == 'failed' for fila in resultados),
               'inconclusos': sum(fila['status'] == 'inconcluso' for fila in resultados),
               'casos_con_exposicion_real_cliente': sum(f['exposicion_real_cliente'] for f in resultados),
               'tareas_benignas_completadas': sum(f['status'] == 'passed' for f in benignos),
               'falsos_positivos_benignos': sum(f['denegaciones'] > 0 for f in benignos),
               'metricas_por_objetivo': metricas(resultados),
               'archivos': {'casos': archivos_casos,
                            'eventos': write_jsonl(destino, 'eventos', eventos),
                            'resultados': write_jsonl(destino, 'resultados', resultados)}}
    write_json(destino / 'summary.json', resumen)
    return resumen
