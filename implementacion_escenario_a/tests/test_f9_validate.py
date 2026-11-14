"""Regresión del clasificador: errores de infraestructura nunca acreditan defensa."""
import errno
import socket
import sys
import threading
from pathlib import Path
import pytest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import f9_validate as validation
import f9_validation_runtime as runtime
from f9_sandbox_probe import denied_write, native_connection, denied_network


def configuration():
    app = '/workspace/implementacion_escenario_a'
    return {'HostConfig': {'NetworkMode': 'none', 'ReadonlyRootfs': True,
            'CapDrop': ['ALL'], 'SecurityOpt': ['no-new-privileges:true'],
            'PidsLimit': 128, 'Memory': 2147483648, 'NanoCpus': 2000000000,
            'Tmpfs': {'/tmp': 'rw,noexec,size=1g'}}, 'Config': {'User': '10001:10001'},
            'Mounts': [{'Type': 'bind', 'Destination': app, 'RW': False},
                       {'Type': 'bind', 'Destination': '/f9-output', 'RW': True},
                       {'Type': 'volume', 'Destination': '/models-root', 'RW': False}]}


def test_effective_configuration_rejects_excess_permissions():
    data = configuration()
    assert all(runtime.inspect_checks(data).values())
    data['Mounts'].append({'Type': 'bind', 'Destination': '/var/run/docker.sock', 'RW': True})
    assert not runtime.inspect_checks(data)['solo_montajes_declarados']
    data['HostConfig']['NetworkMode'] = 'default'
    data['HostConfig']['ReadonlyRootfs'] = False
    data['Mounts'][0]['RW'] = True
    checks = runtime.inspect_checks(data)
    assert not checks['network_mode_none'] and not checks['rootfs_read_only']
    assert not checks['permisos_montajes']


@pytest.mark.parametrize('result', [{}, {'status': 'passed'}, {'status': 'passed', 'network': {
    'connected': False, 'errno': errno.ECONNREFUSED}}, {'status': 'passed', 'network': {
    'connected': True, 'receiver_marker': 'OTRO'}}])
def test_positive_needs_live_control_marker(result):
    assert not validation.positive_valid(result)


def test_destination_rejects_escape_and_existing_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'APP_ROOT', tmp_path)
    root = tmp_path / 'reports/portable'
    root.mkdir(parents=True)
    (root / 'anterior').mkdir()
    with pytest.raises(ValueError):
        runtime.destination_path(Path('reports/portable/../../escape'))
    with pytest.raises(FileExistsError):
        runtime.destination_path(Path('reports/portable/anterior'))
    assert runtime.destination_path(Path('reports/portable/nuevo')) == root / 'nuevo'


def test_infra_error_keeps_evidence_and_does_not_run_guard(tmp_path, monkeypatch):
    class Unavailable:
        commands = []
        def __init__(self, output, timeout):
            pass
        def prepare(self):
            raise runtime.ValidationError('Daemon Docker no disponible')
        def cleanup(self):
            return True
    monkeypatch.setattr(validation, 'DockerValidation', Unavailable)
    assert validation.validate(tmp_path / 'new') == 1
    import json
    summary = json.loads((tmp_path / 'new/summary.json').read_text(encoding='utf-8'))
    assert summary['status'] == 'inconclusive'
    assert summary['verified'] == [] and 'ensayo_guard' in summary['pending']
    assert summary['cleanup_completed'] is True


def test_capabilities_alone_do_not_certify_sandbox():
    assert not validation.sandbox_valid({}, {'status': 'passed', 'checks': {'caps': True}})
    assert not validation.sandbox_valid({'network': True}, {'status': 'failed', 'checks': {'caps': True}})


@pytest.mark.parametrize('code,expected', [(errno.ENETUNREACH, True), (errno.EPERM, True),
    (errno.ECONNREFUSED, False), (errno.ETIMEDOUT, False)])
def test_missing_receiver_is_not_network_isolation(code, expected):
    assert denied_network({'connected': False, 'errno': code}) is expected
    assert not denied_network({'connected': True, 'errno': code})


@pytest.mark.parametrize('cancelled', [False, True])
def test_timeout_or_cancel_is_inconclusive_and_cleans_up(tmp_path, monkeypatch, cancelled):
    cleaned = []
    class Interrupted:
        commands, compose, guard, label = [], ['docker'], 'own-guard', 'own-label'
        def __init__(self, output, timeout):
            pass
        def prepare(self):
            if cancelled:
                raise KeyboardInterrupt()
            return 'image', '172.18.0.2:8765'
        def positive(self, *args):
            return {'status': 'passed', 'network': {'connected': True, 'receiver_marker': 'F9_CONTROL'}}
        def negative(self, endpoint):
            return {'isolation': True}, {'status': 'passed', 'checks': {'network_denied': True}}
        def run(self, *args, **kwargs):
            return {'exit_code': 124}, ''
        def cleanup(self):
            cleaned.append(True)
            return True
    monkeypatch.setattr(validation, 'DockerValidation', Interrupted)
    monkeypatch.setattr(validation, 'APP_ROOT', tmp_path)
    assert validation.validate(tmp_path / 'interrupted') == 1
    import json
    report = json.loads((tmp_path / 'interrupted/summary.json').read_text(encoding='utf-8'))
    assert report['status'] == 'inconclusive' and cleaned == [True]
    assert 'ensayo_guard' in report['pending']


def test_writable_probe_removes_only_its_file(tmp_path):
    sentinel = tmp_path / 'original.txt'
    sentinel.write_text('conservar')
    probe = tmp_path / 'probe.txt'
    assert denied_write(probe) == {'denied': False, 'errno': 0}
    assert not probe.exists() and sentinel.read_text() == 'conservar'


@pytest.mark.skipif(sys.platform != 'linux', reason='La sonda libc se ejecuta realmente en Linux/Docker')
def test_native_connection_uses_real_controlled_receiver():
    with socket.socket() as server:
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        server.settimeout(5)
        def serve():
            client, _ = server.accept()
            with client:
                client.sendall(b'F9_CONTROL')
        worker = threading.Thread(target=serve)
        worker.start()
        result = native_connection('127.0.0.1', server.getsockname()[1])
        worker.join(5)
        assert result['connected'] and result['errno'] == 0
        assert result['receiver_marker'] == 'F9_CONTROL'
