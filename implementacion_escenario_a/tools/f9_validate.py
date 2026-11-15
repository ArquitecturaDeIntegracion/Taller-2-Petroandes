"""Valida F9.2 en Docker dev con un receptor ficticio privado y sandbox real."""
import argparse
import json
from pathlib import Path
from f0_common import write_report
from project_paths import APP_ROOT
from f9_validation_runtime import DockerValidation, ValidationError, destination_path


def positive_valid(result):
    network = result.get('network', {})
    return result.get('status') == 'passed' and network.get('connected') is True and (
           network.get('receiver_marker') == 'F9_CONTROL')


def sandbox_valid(configuration, probe):
    return bool(configuration) and all(configuration.values()) and probe.get('status') == 'passed' and (
           bool(probe.get('checks')) and all(probe['checks'].values()))


def validate(output, timeout=1800):
    output.mkdir(parents=True, exist_ok=False)
    runtime = DockerValidation(output, timeout)
    status, classification, error = 'inconclusive', 'infraestructura_no_verificada', None
    verified, pending = [], ['control_positivo', 'aislamiento_so', 'ensayo_guard']
    try:
        image, endpoint = runtime.prepare()
        positive = runtime.positive(image, endpoint)
        write_report(output / 'network-positive.json', positive, emit=False)
        if not positive_valid(positive):
            raise ValidationError('El control positivo no alcanzó el receptor; no se atribuye bloqueo a la defensa')
        verified.append('control_positivo')
        pending.remove('control_positivo')
        configuration, probe = runtime.negative(endpoint)
        write_report(output / 'sandbox-configuration.json', {'checks': configuration}, emit=False)
        write_report(output / 'sandbox-probe.json', probe, emit=False)
        after = runtime.positive(image, endpoint, 'network-positive-after')
        write_report(output / 'network-positive-after.json', after, emit=False)
        if not positive_valid(after):
            raise ValidationError('El receptor perdió conectividad; aislamiento no concluyente')
        if not sandbox_valid(configuration, probe):
            status, classification = 'failed', 'configuracion_sandbox_no_conforme'
            raise ValidationError('El sandbox no cumple los controles; no se ejecuta el ensayo')
        verified.append('aislamiento_so')
        pending.remove('aislamiento_so')
        report, _ = runtime.run('guard', runtime.compose + ['run', '--rm', '--no-deps', '-T',
            '--name', runtime.guard, '--label', runtime.label, 'f9-sandbox',
            'tools/f9_guard_check.py', '--output-dir', '/f9-output/ensayo'], check=False)
        summary_path = output / 'ensayo/summary.json'
        if not summary_path.is_file() or report['exit_code'] in (124, 126):
            raise ValidationError('Ensayo incompleto o error de infraestructura; revisar guard/command.json')
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        if report['exit_code'] != 0 or summary.get('status') != 'passed':
            status, classification = 'failed', 'ensayo_guard_no_aprobado'
            raise ValidationError('El ensayo guard no aprobó todos sus controles')
        verified.append('ensayo_guard')
        pending.remove('ensayo_guard')
        status, classification = 'passed', 'controles_y_ensayo_verificados'
    except KeyboardInterrupt:
        status, classification = 'inconclusive', 'interrumpido_por_operador'
        error = 'KeyboardInterrupt: se conserva evidencia parcial y se limpian recursos propios'
    except (ValidationError, OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        error = f'{type(exc).__name__}: {exc}'
    finally:
        try:
            cleanup_ok = runtime.cleanup()
        except (OSError, ValueError) as exc:
            cleanup_ok = False
            error = (error or '') + f'; limpieza: {exc}'
        if not cleanup_ok and status == 'passed':
            status, classification = 'inconclusive', 'limpieza_no_completada'
    summary = {'phase': 'F9.2', 'status': status, 'classification': classification,
        'error': error, 'verified': verified, 'pending': pending, 'cleanup_completed': cleanup_ok,
        'controlled_receiver': 'Contenedor propio en red bridge interna; sin puertos publicados ni terceros.',
        'evidence': ['network-positive.json', 'network-positive-after.json',
                     'sandbox-configuration.json', 'sandbox-probe.json',
                     'ensayo/summary.json', 'commands.json'],
        'limitations': ['La sonda nativa prueba el aislamiento frente al receptor controlado.',
            'CapDrop y no-new-privileges no impiden crear subprocess.',
            'No acredita inmunidad a todo documento envenenado ni protege procesos del cliente MCP.']}
    write_report(output / 'commands.json', {'steps': runtime.commands}, emit=False)
    write_report(output / 'summary.json', summary)
    return 0 if status == 'passed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=1800, help='Límite por ensayo en segundos')
    args = parser.parse_args()
    try:
        if args.timeout <= 0:
            raise ValueError('El timeout debe ser positivo')
        output = destination_path(args.output_dir)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    return validate(output, args.timeout)


if __name__ == '__main__':
    raise SystemExit(main())
