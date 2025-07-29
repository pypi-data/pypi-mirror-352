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
import yaml


from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from yaml import *


from .utils import run




GIT_URL = "https://github.com/tianocore/edk2.git"

BASE_DIR = Path(__file__).resolve().parent
config_file = BASE_DIR / "conf" / "target.yaml"






def parse_args():
    parser = argparse.ArgumentParser(description="EDK II Entwicklungsumgebung Setup Tool")
    parser.add_argument("-n", "--name", required=True, help="Name der Entwicklungsumgebung")
    parser.add_argument("-a", "--arch", required=True, choices=["IA32", "X64", "ARM", "AARCH64"], help="Zielarchitektur")
    parser.add_argument("-b", "--build", required=True, help="Zu buildendes Paket oder 'all' für alles")
    parser.add_argument("-t", "--toolchain", default="GCC5", help="Toolchain-Tag, z.B. GCC5")
    parser.add_argument("-p", "--platform", default="MdePkg/MdePkg.dsc", help="Pfad zur Plattform-DSC-Datei")
    parser.add_argument("-r", "--release", default="RELEASE", choices=["RELEASE", "DEBUG"], help="Build-Ziel (RELEASE oder DEBUG)")
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


def load_config(path):

    with open(path, "r") as file:
        return yaml.safe_load(file)


def create_config(edk_dir: Path, arch: str):
    conf_dir = edk_dir / "Conf"
    conf_dir.mkdir(parents=True, exist_ok=True)
    target_txt = conf_dir / "target.txt"
    
    
    config = load_config(config_file)
    active_platform = config.get("active_platform", "")
    target_arch = config.get("target_arch", "")
    tool_chain_tag = config.get("tool_chain_tag", "")
    build_target = config.get("build_target", "")
    
    # Inhalt für target.txt erstellen
    content = f"""ACTIVE_PLATFORM = {active_platform}
TARGET_ARCH = {arch}
TOOL_CHAIN_TAG = {tool_chain_tag}
BUILD_TARGET = {build_target}
"""


    
    # Datei schreiben
    with open(target_txt, "w") as f:
        f.write(content)
    print(f"{target_txt} wurde erstellt.")






def write_target_txt(edk_dir: Path, arch: str):
    conf_dir = edk_dir / "Conf"
    conf_dir.mkdir(parents=True, exist_ok=True)
    target_txt = conf_dir / "target.txt"
    with target_txt.open("w") as f:
        f.write(f"""ACTIVE_PLATFORM       = MdePkg/MdePkg.dsc
TARGET_ARCH           = {arch}
TOOL_CHAIN_TAG        = GCC5
BUILD_TARGET          = RELEASE
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
        "build -p MdePkg/MdePkg.dsc -a X64 -t GCC5 -b RELEASE"
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
        ". ./edksetup.sh",
        "make -C BaseTools"
    ]

    if build_target.lower() == "all":
        commands.append("build")
    else:
        commands.append(f"build -p MdePkg/MdePkg.dsc -m {build_target}")

    full_cmd = " && ".join(commands)
    logging.info(f"[INFO] Baue EDK II mit: {full_cmd}")

    run(full_cmd, shell=True)


def build_edk4(edk_dir: str, build_target: str, arch: str = "X64", toolchain: str = "GCC5", platform_dsc: str = "MdePkg/MdePkg.dsc", release: str = "RELEASE"):
    edk2_path = Path(edk_dir).resolve()
    env = os.environ.copy()
    env["WORKSPACE"] = str(edk2_path)
    env["EDK_TOOLS_PATH"] = str(edk2_path / "BaseTools")
    platforms_path = edk2_path.parent / "edk2-platforms"
    nonosi_path = edk2_path.parent / "edk2-non-osi"

    paths = [edk2_path, platforms_path, nonosi_path]
    valid_paths = [str(p) for p in paths if p.exists()]

    if not valid_paths:
        raise FileNotFoundError("Kein gültiger PACKAGES_PATH gefunden")

    env = os.environ.copy()
    env["WORKSPACE"] = str(edk2_path)
    env["PACKAGES_PATH"] = ":".join(valid_paths)
    env["EDK_TOOLS_PATH"] = str(edk2_path / "BaseTools")
    extras = []
    for name in ["edk2-platforms", "edk2-non-osi"]:
        path = edk2_path.parent / name
        if path.exists():
            extras.append(str(path))
    env["PACKAGES_PATH"] = ":".join([str(edk2_path)] + extras)

    try:
        subprocess.run(["bash", "-c", f". ./edksetup.sh BaseTools"], cwd=edk2_path, env=env, check=True)
        subprocess.run(["make", "-C", "BaseTools"], cwd=edk2_path, env=env, check=True)

        if build_target.lower() == "all":
            cmd = ["build"]
        else:
            cmd = [
                "build",
                "-p", platform_dsc,
                "-m", build_target,
                "-a", arch,
                "-t", toolchain,
                "-b", release
            ]

        subprocess.run(cmd, cwd=edk2_path, env=env, check=True)
        print("✅ Build abgeschlossen.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen: {e}")

        
def build_mdepkg(edk2_root: str):
    """
    Führt den Build-Befehl für MdePkg aus:
    build -a X64 -t GCC5 -b RELEASE -p MdePkg/MdePkg.dsc

    :param edk2_root: Pfad zum EDK2-Verzeichnis
    """
    edk2_path = Path(edk2_root).resolve()
    env = os.environ.copy()
    env["WORKSPACE"] = str(edk2_path)
    env["EDK_TOOLS_PATH"] = str(edk2_path / "BaseTools")

    # Optional: PACKAGES_PATH ergänzen, wenn edk2-platforms etc. vorhanden sind
    extras = []
    for name in ["edk2-platforms", "edk2-non-osi"]:
        path = edk2_path.parent / name
        if path.exists():
            extras.append(str(path))
    env["PACKAGES_PATH"] = ":".join([str(edk2_path)] + extras)

    try:
        # Setup ausführen
        subprocess.run(["bash", "-c", ". ./edksetup.sh BaseTools"], cwd=edk2_path, env=env, check=True)

        # BaseTools kompilieren
        subprocess.run(["make", "-C", "BaseTools"], cwd=edk2_path, env=env, check=True)

        # Build ausführen
        subprocess.run([
            "build",
            "-a", "X64",
            "-t", "GCC5",
            "-b", "RELEASE",
            "-p", "MdePkg/MdePkg.dsc"
        ], cwd=edk2_path, env=env, check=True)

        print("✅ Build erfolgreich abgeschlossen.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen: {e}")


def setup_logging(logfile: Path):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  

    file_handler = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) 
    file_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    coloredlogs.install(
        level='INFO',
        logger=logger,
        fmt='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S'
    )


def exports(workspace: Path):
    os.chdir(str(workspace))
    cwd = os.getcwd()
    os.environ["PACKAGES_PATH"] = f"{cwd}/edk2:{cwd}/edk2-platforms:{cwd}/edk2-non-osi"
    print(os.environ["PACKAGES_PATH"])
    

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
    clone("https://github.com/tianocore/edk2-platforms", edk2_dir)
    clone("https://github.com/tianocore/edk2-non-osi.git", edk2_dir)
    
    exports(workspace)
    
    create_config(edk2_dir, args.arch)
    write_target_txt(edk2_dir, args.arch)
    build_mdepkg(edk2_dir)
#    build_edk4(
#        edk_dir=edk2_dir,
#        build_target=args.build,
#        arch=args.arch,
#        toolchain=args.toolchain,
#        platform_dsc=args.platform,
#        release=args.release
#    )

    #build_edk2(edk2_dir, args.build)
    #build(edk2_dir)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        logging.info(f"[ERROR] Fehler beim Ausführen: {e}")
        sys.exit(1)