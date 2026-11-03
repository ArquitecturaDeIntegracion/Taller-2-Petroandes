"""Ejecuta una sonda real de F0 y registra éxito o fallo sin sustituir motores."""
import argparse
import importlib
import os
import platform
import shutil
import subprocess
import traceback
from time import perf_counter

from f0_common import ROOT, configure_cache, memory, versions, write_report


def environment():
    import psutil
    cpu = platform.processor()
    if os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    node = shutil.which("node")
    result = subprocess.run([node, "--version"], capture_output=True, text=True,
                            check=True) if node else None
    return {"status": "observed", "platform": platform.platform(), "cpu": cpu,
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(), "memory": memory(),
            "node": {"executable": node, "version": result.stdout.strip() if result else None},
            "packages": versions(), "network": "Ver resultados separados de descargas",
            "isolated": os.sys.prefix != os.sys.base_prefix,
            "global_configuration_changed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("probe", choices=["environment", "storage", "e5", "laya"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    configure_cache(args.offline)
    start = perf_counter()
    try:
        if args.probe == "environment":
            report = environment()
        else:
            module = importlib.import_module("f0_" + args.probe)
            if args.probe == "storage":
                report = module.probe()
            elif args.probe == "laya":
                report = module.probe(args.offline, ROOT / args.output)
            else:
                report = module.probe(args.offline)
        code = 0
    except Exception as exc:
        report = {"status": "failed", "exception_type": type(exc).__name__,
                  "error": str(exc), "traceback": traceback.format_exc().splitlines()}
        code = 1
    report.update({"probe": args.probe, "offline_requested": args.offline,
                   "total_seconds": perf_counter() - start, "phase_F0_complete": False})
    write_report(ROOT / args.output, report)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
