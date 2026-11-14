"""Consumidor adversarial determinista: obedece propuestas de fixture, sin detector ni LLM."""
from copy import deepcopy
import json

from .dispatcher import huella


class ClienteForzado:
    def __init__(self, caso, plan, sesion):
        self.caso = caso
        self.plan_sha256 = huella(json.dumps(plan.model_dump(), sort_keys=True))
        self.sesion = sesion
        self.recibidos = ()

    def recibir(self, turno=None):
        """Recibe bytes de texto y preserva origen no confiable en todos los turnos."""
        limite = len(self.caso.fragmentos) if turno is None else min(turno, len(self.caso.fragmentos))
        self.recibidos = tuple({'texto': texto, 'sha256': huella(texto),
                                'procedencia': f'fixture://f9.1/{self.caso.id}/{indice}',
                                'confianza': 'dato_no_confiable', 'turno': indice,
                                'sesion': self.sesion, 'plan_sha256': self.plan_sha256}
                               for indice, texto in enumerate(self.caso.fragmentos[:limite], 1))
        return deepcopy(self.recibidos)

    def proponer(self, turno=None):
        if not self.recibidos:
            raise ValueError('No se pueden proponer acciones sin exposición previa')
        necesarios = len(self.caso.fragmentos) if turno is None else min(turno, len(self.caso.fragmentos))
        if len(self.recibidos) < necesarios:
            raise ValueError('El turno todavía no recibió el fragmento correspondiente')
        # La acción viene del caso declarado; no se infiere ni se ejecuta el texto.
        propuestas = [('herramienta', accion) for accion in self.caso.propuestas]
        if self.caso.borrador is not None:
            propuestas.append(('borrador', self.caso.borrador))
        return deepcopy(propuestas if turno is None else propuestas[turno - 1:turno])
