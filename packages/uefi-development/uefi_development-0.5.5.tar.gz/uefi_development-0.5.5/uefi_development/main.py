#!/usr/bin/env python3
import argparse
import sys
import os
import re 
import pathlib
import subprocess
import shlex
import logging, coloredlogs
import tqdm



from subprocess import Popen, PIPE, STDOUT
from pathlib import Path



from .utils import run




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





def clone(repo_url: str, target_dir: Path):
    success = clone_edk2(repo_url, target_dir)
    if success:
        logging.info("Repository ist bereit.")
    else:
        logging.info("Fehler beim Klonen oder Aktualisieren.")



def clone_edk2(git_url: str, target_dir: Path) -> bool:
    try:
        if target_dir.exists() and target_dir.is_dir():
            logging.info(f"[INFO] Verzeichnis '{target_dir}' existiert bereits.")
            logging.info("[INFO] Aktualisiere Submodule...")
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=str(target_dir),
                check=True
            )
        else:
            logging.info(f"[INFO] Klone Repository {git_url} nach {target_dir} ...")
            subprocess.run(["git", "clone", git_url, str(target_dir)], check=True)
            logging.info("[INFO] Aktualisiere Submodule nach Klonen...")
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=str(target_dir),
                check=True
            )
        return True
    except subprocess.CalledProcessError as e:
        logging.info(f"[ERROR] Git-Befehl fehlgeschlagen: {e}")
        return False



def initialise_submodules(target_dir: Path):
    logging.info("[INFO] Initialisiere und aktualisiere Submodule...")
    run(["git", "pull"], cwd=str(target_dir))
    run(["git", "submodule", "update", "--init", "--recursive"], cwd=str(target_dir))
    run(["git", "pull"], cwd=str(target_dir))






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
    logging.info(f"[INFO] target.txt geschrieben: {target_txt}")




def build(edk_dir: Path):
    edksetup = edk_dir / "edksetup.sh"
    if not edksetup.exists():
        logging.info("[ERROR] edksetup.sh nicht gefunden!")
        sys.exit(1)

    logging.info("[INFO] Setze Build-Umgebung auf...")

    commands = [
        f"cd {edk_dir}",
        ". ./edksetup.sh",
        "build"
    ]

    full_cmd = " && ".join(commands)
    logging.info(f"[INFO] Baue EDK II mit: {full_cmd}")

    run(full_cmd, shell=True)



def build_edk2(edk_dir: Path, build_target: str):
    edksetup = edk_dir / "edksetup.sh"
    if not edksetup.exists():
        logging.info("[ERROR] edksetup.sh nicht gefunden!")
        sys.exit(1)

    logging.info("[INFO] Setze Build-Umgebung auf...")

    commands = [
        f"cd {edk_dir}",
        ". ./edksetup.sh BaseTools",
        "make -C BaseTools",
        "build"
    ]

    if build_target.lower() == "all":
        commands.append("build")
    else:
        commands.append(f"build -p MdePkg/MdePkg.dsc -m {build_target}")

    full_cmd = " && ".join(commands)
    logging.info(f"[INFO] Baue EDK II mit: {full_cmd}")

    run(full_cmd, shell=True)


def setup_logging(logfile: Path):
    # Root-Logger holen
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Alle Level erfassen

    # File-Handler (build.log)
    file_handler = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # alles in die Datei
    file_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Coloredlogs für die Konsole
    coloredlogs.install(
        level='INFO',
        logger=logger,
        fmt='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    args = parse_args()

    home = Path.home()
    workspace = home / args.name
    workspace.mkdir(parents=True, exist_ok=True)

    logfile = workspace / "build.log"
    setup_logging(logfile)

    logging.info(f"Projektverzeichnis: {workspace}")
    os.chdir(workspace)
    logging.info(f"Arbeitsverzeichnis gewechselt zu: {workspace}")
    
    edk2_dir = workspace / "edk2"

    clone(GIT_URL, edk2_dir)
    write_target_txt(edk2_dir, args.arch)
    build_edk2(edk2_dir, args.build)
    build(edk2_dir)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        logging.info(f"[ERROR] Fehler beim Ausführen: {e}")
        sys.exit(1)