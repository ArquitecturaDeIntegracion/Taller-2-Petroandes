"""Medición diagnóstica con el checkpoint multilingüe fijado en F0."""
from importlib.metadata import version
from math import isfinite
from time import perf_counter

from f0_laya import LayaPairTooLong, MODEL, REVISION, check_pair, model_snapshot

THRESHOLD = 0.5
LIMITS = {"max_len": 1024, "head_max_len": 256}
SUPPORT = {"type": "noul", "instructions":
           "¿La evidencia respalda íntegramente la afirmación, incluidas cifras y condiciones?"}
RELEVANCE = {"type": "choice", "instructions": "¿El fragmento aporta evidencia para responder la consulta?",
             "criteria": {"pertinente": "Aporta evidencia directa o contexto necesario",
                          "no_pertinente": "No aporta evidencia necesaria para la consulta"}}


class Judge:
    def __init__(self):
        import laya
        import torch

        started = perf_counter()
        torch.set_num_threads(2)
        self.agent = laya.load(model_snapshot(offline=True), device="cpu", backend="eager")
        self.configuration = {"paquete": version("laya"), "modelo": MODEL, "revision": REVISION,
                              "device": str(self.agent.device), "backend": self.agent.backend,
                              "hilos": 2, "carga_ms": (perf_counter() - started) * 1000,
                              "limites": LIMITS, "pregunta_anclaje": SUPPORT, "pregunta_pertinencia": RELEVANCE,
                              "umbral_diagnostico": THRESHOLD, "umbral_calibrado": None}

    def assess(self, state, question):
        started = perf_counter()
        try:
            tokens, _ = check_pair(self.agent, state, question)
            result = self.agent.predict(state, {"juicio": question}, **LIMITS)["answers"]["juicio"]
            if question["type"] == "noul":
                probability = result["noul"]
                if not isfinite(probability) or not 0 <= probability <= 1:
                    raise ValueError("Probabilidad de laya fuera del intervalo")
                observation = {"probabilidad": probability, "positivo": probability >= THRESHOLD}
            else:
                choice, probabilities = result["choice"], result["probabilities"]
                if (choice not in RELEVANCE["criteria"] or probabilities.keys() != RELEVANCE["criteria"].keys()
                        or not all(isfinite(value) and 0 <= value <= 1 for value in probabilities.values())):
                    raise ValueError("Salida choice inválida")
                observation = {"eleccion": choice, "probabilidades": probabilities, "positivo": choice == "pertinente"}
            return {"estado": "evaluado", "tokens": tokens, "ms": (perf_counter() - started) * 1000, **observation}
        except LayaPairTooLong:
            return {"estado": "no_evaluable", "motivo": "excede_limite_tokens"}
        except (RuntimeError, ValueError, KeyError) as exc:
            return {"estado": "error", "tipo": type(exc).__name__, "motivo": str(exc)}

    def support(self, claim, evidence):
        return self.assess(f"Afirmación:\n{claim}\nEvidencia citada:\n{evidence}", SUPPORT)

    def relevance(self, query, fragment):
        return self.assess(f"Consulta:\n{query}\nFragmento:\n{fragment}", RELEVANCE)
