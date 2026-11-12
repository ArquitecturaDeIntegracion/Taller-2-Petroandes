"""Registra la sustitución revisada y su evento en la misma transacción."""
from petroandes.governance.models import Observation, Relation
from .documents import validate_sources
from .store import document_key


def substitute(store, observation, relation, reviewer, expected_revision):
    observation = Observation.model_validate_json(observation.model_dump_json())
    relation = Relation.model_validate_json(relation.model_dump_json())
    if (store.perfil != "laboratorio" or not isinstance(reviewer, str) or not reviewer.strip()
            or observation.estado != "excluido" or observation.documento != relation.hacia
            or relation.desde == relation.hacia or relation.evidencia.fuente != relation.desde
            or relation.evidencia not in observation.fuentes):
        raise ValueError("La sustitución requiere revisión explícita, sucesor y evidencia de exclusión")

    def mutation(_revision):
        db = store.db
        key = document_key(observation.documento)
        if db.execute("SELECT pdf_sha256 FROM documents WHERE document_key=?", (key,)).fetchone() != (
                observation.pdf_sha256,):
            raise ValueError("La exclusión no corresponde a la huella actual del documento anterior")
        validate_sources(db, observation.fuentes)
        prior = db.execute("SELECT payload FROM observations WHERE observation_id=?",
                           (observation.observation_id,)).fetchone()
        link = db.execute("SELECT payload FROM relations WHERE relation_id=?", (relation.relation_id,)).fetchone()
        if prior and link and Observation.model_validate_json(prior[0]) == observation and (
                Relation.model_validate_json(link[0]) == relation):
            return False
        if prior or link:
            raise ValueError("Identificador de sustitución ya registrado con otros datos")
        db.execute("INSERT INTO observations VALUES (?,?,?,?)", (observation.observation_id, key,
                   observation.pdf_sha256, observation.model_dump_json()))
        db.execute("INSERT INTO relations VALUES (?,?)", (relation.relation_id, relation.model_dump_json()))
        return True

    payload = {"relation_id": relation.relation_id, "observation_id": observation.observation_id,
               "anterior": relation.hacia.model_dump(mode="json"), "sucesor": relation.desde.model_dump(mode="json"),
               "revisor_humano": reviewer.strip()}
    return store.change(expected_revision, "documento.sustituido", payload, mutation)
