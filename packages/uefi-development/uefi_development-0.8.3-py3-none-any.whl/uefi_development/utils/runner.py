def run_multiple_linux_commands_realtime(commands: list[str], cwd=None, env=env, shell=True) -> bool:
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