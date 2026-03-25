#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path


def find_mlx_whisper():
    candidates = [
        shutil.which('mlx_whisper'),
        str(Path.home() / 'Library' / 'Python' / '3.9' / 'bin' / 'mlx_whisper'),
        str(Path.home() / '.local' / 'bin' / 'mlx_whisper'),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def check(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        first = (out.stdout or out.stderr).strip().splitlines()
        return True, (first[0] if first else 'ok')
    except Exception as e:
        return False, str(e)


def main():
    results = {}
    results['python3'] = (shutil.which('python3') is not None, sys.version.split('\n')[0])
    results['ffmpeg'] = check(['ffmpeg', '-version']) if shutil.which('ffmpeg') else (False, 'not found')
    results['ffprobe'] = check(['ffprobe', '-version']) if shutil.which('ffprobe') else (False, 'not found')
    mlx = find_mlx_whisper()
    results['mlx_whisper'] = check([mlx, '--help']) if mlx else (False, 'not found')
    results['swift'] = check(['swift', '--version']) if shutil.which('swift') else (False, 'not found')

    ok = True
    for name, (passed, info) in results.items():
        mark = 'OK' if passed else 'MISSING'
        print(f'{mark:8} {name:12} {info}')
        ok = ok and passed
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
