from uuid import uuid4

from petroandes.contracts.documents import Fragment
from petroandes.contracts.queries import FragmentQuery
from petroandes.retrieve.ranking import fuse
from petroandes.retrieve.selection import direct_parts


def test_ambiguous_authorized_emissions_require_hash_before_selecting_section():
    def emission(hash_value, section):
        return Fragment(doc_id="SIN-VERSION", version_documental=None, pdf_sha256=hash_value * 64,
            chunk_id=str(uuid4()), section_id=section, titulo_seccion=section, pagina_inicio=1, pagina_fin=1,
            parte=1, orden=0, parent_id=None, texto="Parte de prueba.", parser_version="fixture-1",
            particion="structural-es-1.0.0", bundle="e5small-es-1.0.0", tokens_entrada=10)

    first = emission("a", "seccion-1")
    second = emission("b", "seccion-2")
    records = {part.chunk_id: (part, {}) for part in (first, second)}
    query = FragmentQuery(doc_id="SIN-VERSION", version_documental=None, section_id="seccion-1")
    assert direct_parts(query, records) is None
    assert direct_parts(query.model_copy(update={"pdf_sha256": first.pdf_sha256}), records) == [first]
    assert direct_parts(query.model_copy(update={"pdf_sha256": second.pdf_sha256}), records) == []


def test_rrf_deduplicates_by_id_and_breaks_rank_ties():
    assert fuse(["a", "b", "a"], ["b", "a"], {"b"}, 2) == ["b", "a"]
    assert fuse(["b", "a"], ["a", "b"], set(), 1) == ["a"]
