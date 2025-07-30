import subprocess 
import shlex
from subprocess import Popen, PIPE, STDOUT


def run_command_realtime(command: str, cwd=None, env=None, shell=True) -> int:
    """
    Führt einen einzelnen Linux-Befehl aus und zeigt seine Ausgabe in Echtzeit an.

    Args:
        command: Der Befehl, der ausgeführt werden soll (als String).

    Returns:
        Der Exit-Code des ausgeführten Befehls.
    """
    print(f"Executing command: '{command}'")
    try:
        # shlex.split wird verwendet, um den Befehl sicher in eine Liste von Argumenten aufzuteilen.
        # Dies ist wichtig, um Shell-Injection-Probleme zu vermeiden und korrekte Argumente zu übergeben.
        # shell=True sollte vermieden werden, es sei denn, es ist absolut notwendig,
        # da es Sicherheitsrisiken birgt und plattformabhängige Verhaltensweisen verursachen kann.
        process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Leitet stderr zu stdout um, um alles zusammen zu sehen
            text=True,                 # Dekodiert die Ausgabe als Text (UTF-8 Standard)
            bufsize=1                  # Zeilenweise Pufferung für Echtzeit-Ausgabe
        )

        # Liest die Ausgabe Zeile für Zeile und druckt sie aus
        for line in process.stdout:
            print(line, end='') # 'end='': Verhindert zusätzliche Newlines, da 'line' bereits eine enthält

        # Wartet, bis der Prozess abgeschlossen ist und gibt den Exit-Code zurück
        return_code = process.wait()
        print(f"Command '{command}' finished with exit code: {return_code}")
        return return_code

    except FileNotFoundError:
        print(f"Error: Command '{command.split()[0]}' not found.")
        return 127  # Typischer Exit-Code für "command not found"
    except Exception as e:
        print(f"An error occurred while executing command '{command}': {e}")
        return 1
    
def run_multiple_linux_commands_realtime(commands: list[str], cwd=None, env=None, shell=True) -> bool:
    """
    Führt eine Liste von Linux-Befehlen sequenziell aus und zeigt deren Ausgabe in Echtzeit an.
    Die Ausführung stoppt, wenn ein Befehl fehlschlägt (non-zero exit code).

    Args:
        commands: Eine Liste von Strings, wobei jeder String ein Linux-Befehl ist.

    Returns:
        True, wenn alle Befehle erfolgreich ausgeführt wurden, False sonst.
    """
    print("\n--- Starting execution of multiple commands ---")
    for i, command in enumerate(commands):
        print(f"\n--- Command {i+1}/{len(commands)} ---")
        exit_code = run_command_realtime(command)
        if exit_code != 0:
            print(f"Error: Command '{command}' failed with exit code {exit_code}. Stopping execution.")
            return False
    print("\n--- All commands executed successfully ---")
    return True