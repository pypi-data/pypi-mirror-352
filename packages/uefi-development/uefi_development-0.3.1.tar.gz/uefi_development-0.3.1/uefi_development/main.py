#!/usr/bin/env python3
import argparse
import os
import sys
import re
import subprocess
import pathlib
import tqdm
import re
import shlex
import time
import logging

from subprocess import Popen, PIPE, STDOUT
from time import sleep
from pathlib import Path
from tqdm import *

GIT_URL = "https://github.com/tianocore/edk2.git"


def parse_args():
    parser = argparse.ArgumentParser(description="EDK II Entwicklungsumgebung Setup Tool")
    parser.add_argument("-n", "--name", required=True, help="Name der Entwicklungsumgebung")
    parser.add_argument(
        "-a", "--arch", required=True, choices=["IA32", "X64", "ARM", "AARCH64"], help="Zielarchitektur"
    )
    parser.add_argument(
        "-b", "--build", required=True, help="Zu buildendes Paket oder 'all' für alles"
    )
    return parser.parse_args()


def run(commands, edk2_dir):
    """
    Führt eine Liste von Kommandos in edk2_dir aus und gibt die Ausgabe in Echtzeit aus.

    :param commands: Liste von Kommandos, jedes Kommando als Liste von Strings.
    :param edk2_dir: Zielverzeichnis, in dem die Kommandos ausgeführt werden.
    :raises: subprocess.CalledProcessError bei Fehlern.
    """
    if not os.path.isdir(edk2_dir):
        raise FileNotFoundError(f"Zielverzeichnis nicht gefunden: {edk2_dir}")

    for cmd in commands:
        print(f"\n📦 Starte: {' '.join(cmd)} im Verzeichnis {edk2_dir}")
        # Prozess starten
        process = subprocess.Popen(
            cmd,
            cwd=edk2_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Ausgabe Zeile für Zeile in Echtzeit ausgeben
        for line in process.stdout:
            print(line, end='')  # schon mit Zeilenumbruch aus line

        process.stdout.close()
        retcode = process.wait()
        if retcode != 0:
            raise subprocess.CalledProcessError(retcode, cmd)




def clone_source(target_dir: Path):
    if target_dir.exists() and target_dir.is_dir():
        print(f"[INFO] Verzeichnis '{target_dir}' existiert bereits. Klonen wird übersprungen.")
        return True

    print(f"[INFO] Klone Repository {GIT_URL} nach {target_dir}...")
    try:
        subprocess.run(["git", "clone", GIT_URL, str(target_dir)], check=True)
        commands = [
            ["git", "submodule", "update", "--init", "--recursive"],
            ["git", "pull"]
        ]

        run(commands, edk_dir)
        return True  # Jetzt wurde geklont, also auch True


    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Klonen fehlgeschlagen: {e}")
        return False





def build_edk2(edk_dir: Path, build_target: str):
    edksetup = edk_dir / "edksetup.sh"
    if not edksetup.exists():
        print("[ERROR] edksetup.sh nicht gefunden!")
        sys.exit(1)

    print("[INFO] Setze Build-Umgebung auf...")

    # Shell-Befehl zusammenbauen
    if build_target.lower() == "all":
        build_cmd = "build"
    else:
        build_cmd = f"build -p MdePkg/MdePkg.dsc -m {build_target}"

    cmd = f"""
    cd {edk_dir} && \
    . ./edksetup.sh BaseTools && \
    make -C BaseTools && \
    {build_cmd}
    """

    
    commands = [
        ["cd", f"{edk_dir}"],
        [".", "./edksetup.sh", "BaseTools"],
        ["make", "-C", "BaseTools"],
        [f"{build_cmd}"]
    ]

    run(commands, edk_dir)

def write_target_txt(edk_dir: Path, arch: str):
    conf_dir = edk_dir / "Conf"
    conf_dir.mkdir(parents=True, exist_ok=True)
    target_txt = conf_dir / "target.txt"
    with target_txt.open("w") as f:
        f.write(f"""ACTIVE_PLATFORM       = MdePkg/MdePkg.dsc
TARGET_ARCH           = {arch}
TOOL_CHAIN_TAG        = GCC5
BUILD_RULE_CONF       = $(EDK_TOOLS_PATH)/BuildRule/GccRules.mk
""")
    print(f"[INFO] target.txt geschrieben: {target_txt}")




def main():
    args = parse_args()

    home = Path.home()
    workspace = home / args.name
    print(f"[INFO] Projektverzeichnis: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)

    os.chdir(workspace)
    print(f"[INFO] Arbeitsverzeichnis gewechselt zu: {workspace}")

    edk2_dir = workspace / "edk2"

    clone_source(edk2_dir)
    write_target_txt(edk2_dir, args.arch)
    build_edk2(edk2_dir, args.build)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Fehler beim Ausführen: {e}")
        sys.exit(1)
