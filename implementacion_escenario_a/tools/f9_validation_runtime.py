"""Orquestación y evidencia del control TCP privado y el sandbox Docker F9.1."""
import json
import os
from pathlib import Path
from uuid import uuid4
from project_paths import APP_ROOT
from record_command import record

MARKER = 'F9_CONTROL'
RECEIVER = """import socket
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('0.0.0.0',8765)); s.listen(16)
while True:
 c,_=s.accept()
 with c: c.sendall(b'F9_CONTROL')
"""
READY = """import socket,time
for attempt in range(50):
 try:
  with socket.create_connection(('127.0.0.1',8765),timeout=1) as s:
   assert s.recv(64)==b'F9_CONTROL'
  print('F9_CONTROL'); break
 except (OSError,AssertionError): time.sleep(.1)
else: raise SystemExit('Receptor no disponible')
"""


class ValidationError(RuntimeError):
    pass


def destination_path(value):
    root = (APP_ROOT / 'reports/portable').resolve()
    target = (APP_ROOT / value).resolve()
    if not target.is_relative_to(root) or target == root:
        raise ValueError('La salida debe estar dentro de reports/portable')
    if target.exists():
        raise FileExistsError('La salida ya existe; use un nombre nuevo')
    return target


def inspect_checks(data):
    """Comprueba configuración efectiva del contenedor, además de las sondas SO."""
    host, config, mounts = data['HostConfig'], data['Config'], data['Mounts']
    app = '/workspace/implementacion_escenario_a'
    allowed = {app: False, '/f9-output': True, '/models-root': False}
    mounted = {mount['Destination']: mount for mount in mounts if mount['Type'] != 'tmpfs'}
    return {'network_mode_none': host.get('NetworkMode') == 'none',
            'rootfs_read_only': host.get('ReadonlyRootfs') is True,
            'user_10001': config.get('User') == '10001:10001',
            'cap_drop_all': 'ALL' in [x.upper() for x in (host.get('CapDrop') or [])],
            'no_new_privileges': any(x in ('no-new-privileges', 'no-new-privileges:true')
                                      for x in (host.get('SecurityOpt') or [])),
            'pids_limit': 0 < (host.get('PidsLimit') or 0) <= 128,
            'memory_limit': 0 < (host.get('Memory') or 0) <= 2 * 1024 ** 3,
            'cpu_limit': 0 < (host.get('NanoCpus') or 0) <= 2 * 10 ** 9,
            'tmpfs_tmp': '/tmp' in (host.get('Tmpfs') or {}),
            'solo_tmpfs_temporal': all(m['Destination'] == '/tmp' for m in mounts if m['Type'] == 'tmpfs'),
            'solo_montajes_declarados': set(mounted) == set(allowed),
            'permisos_montajes': all(dest in mounted and mounted[dest]['RW'] == rw
                                     for dest, rw in allowed.items()),
            'fuente_bind_proyecto': mounted.get(app, {}).get('Type') == 'bind',
            'reporte_bind': mounted.get('/f9-output', {}).get('Type') == 'bind'}


class DockerValidation:
    def __init__(self, output, timeout):
        self.output, self.timeout, self.sequence = output, timeout, 0
        self.token = uuid4().hex
        self.network = 'petroandes-f9-' + self.token
        self.receiver = self.network + '-receiver'
        self.sandbox = self.network + '-sandbox'
        self.guard = self.network + '-guard'
        self.control = self.network + '-control'
        self.names = [self.control, self.guard, self.sandbox, self.receiver]
        self.compose = ['docker', 'compose', '-f', str(APP_ROOT / 'compose.yaml'), '--profile', 'dev']
        self.commands = []
        self.label = 'petroandes.f9.run=' + self.token

    def run(self, title, command, *, check=True, timeout=None):
        self.sequence += 1
        target = self.output / f'{self.sequence:02d}-{title}'
        environment = {**os.environ, 'PETROANDES_F9_OUTPUT_HOST': str(self.output.resolve())}
        report, stdout, stderr = record(command, target, timeout or self.timeout, env=environment)
        self.last_stderr = stderr
        self.commands.append({'step': title, 'exit_code': report['exit_code'],
                              'evidence': target.relative_to(APP_ROOT).as_posix() + '/command.json'})
        if check and report['exit_code']:
            raise ValidationError(f'{title}: código {report["exit_code"]}; consulte la evidencia')
        return report, stdout

    def prepare(self):
        _, image = self.run('image', self.compose + ['config', '--images', 'f9-sandbox'])
        image = image.strip().splitlines()
        if len(image) != 1:
            raise ValidationError('No se pudo resolver una única imagen para f9-sandbox')
        self.run('network-create', ['docker', 'network', 'create', '--internal',
                                    '--label', self.label, self.network])
        self.run('receiver-start', ['docker', 'run', '--detach', '--name', self.receiver,
                 '--label', self.label, '--network', self.network, image[0], '-c', RECEIVER])
        self.ready('receiver-ready')
        _, endpoint = self.run('receiver-address', ['docker', 'inspect', '--format',
             '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', self.receiver])
        endpoint = endpoint.strip() + ':8765'
        return image[0], endpoint

    def ready(self, title):
        _, stdout = self.run(title, ['docker', 'exec', self.receiver, 'python', '-c', READY], timeout=30)
        if stdout.strip() != MARKER:
            raise ValidationError('El receptor no confirmó su marcador ficticio')

    def positive(self, image, endpoint, title='network-positive'):
        _, stdout = self.run(title, ['docker', 'run', '--rm', '--name', self.control,
             '--label', self.label, '--network', self.network, '--mount',
             f'type=bind,source={APP_ROOT},target=/workspace/implementacion_escenario_a,readonly',
             '--workdir', '/workspace/implementacion_escenario_a', image,
             'tools/f9_sandbox_probe.py', '--receiver', endpoint, '--network-only'], timeout=60)
        return json.loads(stdout)

    def negative(self, endpoint):
        self.run('sandbox-start', self.compose + ['run', '--rm', '--no-deps', '-T', '-d',
                 '--name', self.sandbox, '--label', self.label, 'f9-sandbox', '-c',
                 'import time; time.sleep(180)'], timeout=60)
        _, data = self.run('sandbox-inspect', ['docker', 'inspect', self.sandbox])
        settings = json.loads(data)[0]
        report, stdout = self.run('sandbox-probe', ['docker', 'exec', self.sandbox, 'python',
             'tools/f9_sandbox_probe.py', '--receiver', endpoint], check=False, timeout=60)
        if report['exit_code'] not in (0, 1):
            raise ValidationError('No se completó la sonda del sandbox')
        self.ready('receiver-still-ready')
        return inspect_checks(settings), json.loads(stdout)

    def cleanup(self):
        results = []
        for kind, name in [('container', x) for x in self.names] + [('network', self.network)]:
            template = '{{index .Config.Labels "petroandes.f9.run"}}' if kind == 'container' else (
                       '{{index .Labels "petroandes.f9.run"}}')
            report, stdout = self.run('cleanup-inspect-' + name.rsplit('-', 1)[-1],
                ['docker', kind, 'inspect', '--format', template, name], check=False, timeout=30)
            if report['exit_code'] == 0 and stdout.strip() == self.token:
                command = ['docker', kind, 'rm'] + (['--force'] if kind == 'container' else []) + [name]
                removed, _ = self.run('cleanup-' + kind, command, check=False, timeout=30)
                results.append(removed['exit_code'] == 0)
            elif report['exit_code'] == 0:
                results.append(False)
            elif not any(message in self.last_stderr.lower() for message in
                         ('no such object', 'no such container', 'no such network')):
                results.append(False)
        return all(results)
