"""Regresión técnica de filas y condiciones contrastadas visualmente en el PDF."""
from petroandes.extract.pdf import extract_pdf
from petroandes.paths import PROJECT_ROOT


def sections(relative):
    _, result, _ = extract_pdf(PROJECT_ROOT / "corpus/pdf" / relative)
    return {section.section_id: section for section in result}


def first_table(section):
    return next(block.table for block in section.blocks if block.table)


def test_maop_and_alarm_rows_stay_in_their_document_and_columns():
    manual = sections("01_manuales/MAN-OPE-001_v3.pdf")
    alarms = sections("02_procedimientos/PRO-OPE-012_v3.pdf")
    equipment = sections("06_fichas/FIC-ACT-P101_v2.pdf")
    maop = first_table(manual["3"])
    assert maop.headers[3] == "MAOP (psi)" and maop.rows[0][3] == "1.250"
    assert maop.rows[1][0] == "Barrancabermeja – Ayacucho"
    assert first_table(alarms["3"]).rows[0] == ("Ayacucho – Coveñas", "1.100", "15 minutos", "Alta")
    design = first_table(equipment["2"])
    assert design.headers == ("Parámetro", "Valor de diseño", "Límite de alarma")
    assert design.rows[1] == ("Presión de descarga", "1.180 psi", "1.240 psi")


def test_tolerance_and_uncertainty_are_not_conflated():
    measurement = sections("02_procedimientos/PRO-MED-007_v2.pdf")
    regulation = sections("03_normativa/RES-CREG-0043-2024.pdf")
    assert first_table(measurement["3"]).rows[0] == ("Tolerancia de conciliación", "0,5 % del volumen recibido")
    assert "0,3 %" in regulation["articulo-2"].blocks[0].text
    assert "Incertidumbre" in regulation["articulo-2"].title


def test_sequence_has_all_five_complete_advance_criteria():
    sequence = first_table(sections("02_procedimientos/PRO-OPE-021_v1.pdf")["3"])
    assert [row[0] for row in sequence.rows] == ["1", "2", "3", "4", "5"]
    assert sequence.rows[2][2] == "Vibración por debajo del límite de alarma"
    assert sequence.rows[3][1] == "Apertura progresiva de la válvula de descarga"
    assert sequence.rows[3][2] == "Incremento de caudal sin golpe de ariete"
