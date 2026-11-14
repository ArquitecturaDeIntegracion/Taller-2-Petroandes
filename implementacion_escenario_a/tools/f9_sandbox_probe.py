"""Sondas Linux de aislamiento: SO y conexión TCP nativa a un receptor de prueba."""
import argparse
import ctypes
import errno
import json
import os
import socket
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4


class Address(ctypes.Structure):
    _fields_ = [('family', ctypes.c_ushort), ('port', ctypes.c_ushort),
                ('address', ctypes.c_ubyte * 4), ('zero', ctypes.c_ubyte * 8)]


class Timeval(ctypes.Structure):
    _fields_ = [('seconds', ctypes.c_long), ('microseconds', ctypes.c_long)]


def native_connection(host, port):
    """No utiliza socket.connect de Python ni su audit hook."""
    library = ctypes.CDLL(None, use_errno=True)
    library.socket.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    library.connect.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint]
    library.close.argtypes = [ctypes.c_int]
    library.setsockopt.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_void_p, ctypes.c_uint]
    library.recv.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
    library.recv.restype = ctypes.c_ssize_t
    descriptor = library.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    if descriptor < 0:
        code = ctypes.get_errno()
        return {'connected': False, 'errno': code, 'error': os.strerror(code), 'stage': 'socket'}
    address = Address(family=socket.AF_INET, port=socket.htons(port))
    address.address[:] = socket.inet_aton(host)
    try:
        timeout = Timeval(3, 0)
        for option in (socket.SO_SNDTIMEO, socket.SO_RCVTIMEO):
            if library.setsockopt(descriptor, socket.SOL_SOCKET, option, ctypes.byref(timeout),
                                  ctypes.sizeof(timeout)) != 0:
                raise OSError(ctypes.get_errno(), 'No se pudo limitar la sonda TCP')
        status = library.connect(descriptor, ctypes.byref(address), ctypes.sizeof(address))
        code = ctypes.get_errno() if status else 0
        received = ''
        if status == 0:
            buffer = ctypes.create_string_buffer(64)
            length = library.recv(descriptor, buffer, len(buffer), 0)
            received = buffer.raw[:max(0, length)].decode('ascii', errors='replace')
        return {'connected': status == 0, 'errno': code, 'error': os.strerror(code) if code else None,
                'receiver_marker': received, 'destination': f'{host}:{port}',
                'implementation': 'libc socket/connect/recv'}
    finally:
        library.close(descriptor)


def process_status():
    fields = {}
    for line in Path('/proc/self/status').read_text().splitlines():
        name, _, value = line.partition(':')
        if name in ('NoNewPrivs', 'CapEff'):
            fields[name] = value.strip()
    return fields


def rootfs_read_only():
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        fields = line.split()
        if fields[4] == '/':
            return 'ro' in fields[5].split(',')
    return False


def denied_write(path):
    try:
        path.write_bytes(b'Sonda ficticia F9')
    except OSError as exc:
        return {'denied': exc.errno in (errno.EROFS, errno.EACCES, errno.EPERM), 'errno': exc.errno}
    path.unlink()
    return {'denied': False, 'errno': 0}


def cgroup_value(name):
    path = Path('/sys/fs/cgroup') / name
    return path.read_text().strip() if path.is_file() else None


def denied_network(network):
    return not network['connected'] and network['errno'] in (
        errno.ENETUNREACH, errno.EHOSTUNREACH, errno.EACCES, errno.EPERM)


def inspect_sandbox(host, port):
    identifier = uuid4().hex
    status = process_status()
    root_write = denied_write(Path('/f9-probe-' + identifier))
    source_write = denied_write(Path(__file__).resolve().parents[1] / ('f9-probe-' + identifier))
    with NamedTemporaryFile(prefix='f9-probe-', dir='/tmp') as temporary:
        temporary.write(b'dato ficticio')
        temporary.flush()
        temporary_ok = Path(temporary.name).read_bytes() == b'dato ficticio'
    network = native_connection(host, port)
    mounts = {line.split()[4] for line in Path('/proc/self/mountinfo').read_text().splitlines()}
    credentials = [key for key in os.environ if key in
                   ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AZURE_CLIENT_SECRET', 'HF_TOKEN', 'OPENAI_API_KEY')]
    checks = {'usuario_no_privilegiado': os.getuid() != 0,
              'sin_privilegios_nuevos': status.get('NoNewPrivs') == '1',
              'capacidades_efectivas_vacias': int(status.get('CapEff', '1'), 16) == 0,
              'raiz_solo_lectura': rootfs_read_only(), 'escritura_raiz_denegada': root_write['denied'],
              'fuente_solo_lectura': source_write['denied'], 'temporal_escribible': temporary_ok,
              'sin_socket_docker': not Path('/var/run/docker.sock').exists(),
              'sin_volumen_artifacts': '/workspace/petroandes-data/artifacts' not in mounts,
              'sin_montajes_sensibles_conocidos': not mounts.intersection(('/root/.aws', '/root/.ssh', '/host')),
              'sin_credenciales_en_entorno': not credentials,
              'red_sin_ruta_al_receptor': denied_network(network)}
    return {'status': 'passed' if all(checks.values()) else 'failed', 'uid': os.getuid(),
            'process_status': status, 'root_write': root_write, 'source_write': source_write,
            'network': network, 'checks': checks, 'cgroups': {name: cgroup_value(name) for name in
             ('memory.max', 'pids.max', 'cpu.max')},
            'limitacion': 'No demuestra bloqueo universal de subprocess ni aislamiento del cliente externo.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receiver', required=True, help='IPv4:puerto del receptor controlado')
    parser.add_argument('--network-only', action='store_true')
    args = parser.parse_args()
    host, port = args.receiver.rsplit(':', 1)
    socket.inet_aton(host)
    if args.network_only:
        network = native_connection(host, int(port))
        passed = network['connected'] and network['receiver_marker'] == 'F9_CONTROL'
        result = {'status': 'passed' if passed else 'failed', 'network': network}
    else:
        result = inspect_sandbox(host, int(port))
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
