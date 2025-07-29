#!/usr/bin/env python3
import sys
from pathlib import Path
from orlang.runner import run_orlang

def main():
    if len(sys.argv) < 2:
        print("Usage: orlang <filename.orl>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    source_code = file_path.read_text()
    run_orlang(source_code)

if __name__ == "__main__":
    main() 