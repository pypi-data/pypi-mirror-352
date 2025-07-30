import subprocess
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: lz <inputfile>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print("Error: File not found")
        sys.exit(1)

    with file_path.open() as f:
        input_data = f.read().strip()

    try:
        cmd = f'ssh -p 80 ubuntu@4.156.195.94 "python3 ~/p.py \\"{input_data}\\""'
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print("SSH Error:", e)
