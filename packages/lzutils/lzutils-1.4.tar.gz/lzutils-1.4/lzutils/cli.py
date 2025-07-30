import subprocess
import sys
from pathlib import Path
import shlex

def main():
    if len(sys.argv) != 2:
        print("Usage: lz <inputfile>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)

    try:
        input_data = file_path.read_text().strip()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    safe_input = shlex.quote(input_data)

    ssh_host = "ubuntu@4.156.195.94"
    remote_cmd = f"python3 ~/p.py {safe_input}"
    ssh_cmd = f'ssh {ssh_host} {shlex.quote(remote_cmd)}'

    try:
        subprocess.run(ssh_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"SSH command failed with exit code {e.returncode}")
    except Exception as e:
        print(f"SSH Error: {e}")
