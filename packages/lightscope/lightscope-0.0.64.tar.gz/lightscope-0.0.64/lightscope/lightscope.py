#!/usr/bin/env python3
import sys, time, signal, subprocess, urllib.request, json
from importlib import metadata
from packaging.version import parse as parse_version

CHECK_INTERVAL = 60*60
PYPI_JSON_URL = "https://pypi.org/pypi/lightscope/json"

def get_installed_version():
    try:
        return metadata.version("lightscope")
    except metadata.PackageNotFoundError:
        return None

def get_latest_version():
    try:
        with urllib.request.urlopen(PYPI_JSON_URL) as r:
            return json.load(r)["info"]["version"]
    except:
        return None

def install_or_upgrade():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "lightscope"])

def spawn_app():
    # this runs: python3 -m lightscope
    return subprocess.Popen([sys.executable, "-m", "lightscope"])

def graceful_shutdown(p, timeout=30):
    p.send_signal(signal.SIGTERM)
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()

def main():
    v0 = get_installed_version()
    if not v0:
        install_or_upgrade()
        v0 = get_installed_version()
        if not v0:
            sys.exit("install failed")

    proc = spawn_app()
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            latest = get_latest_version()
            if latest and parse_version(latest) > parse_version(v0):
                graceful_shutdown(proc)
                install_or_upgrade()
                v0 = get_installed_version()
                proc = spawn_app()
    except KeyboardInterrupt:
        graceful_shutdown(proc)

if __name__ == "__main__":
    main()

