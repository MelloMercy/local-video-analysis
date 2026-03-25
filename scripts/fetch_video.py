#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def find_ytdlp():
    candidates = [
        shutil.which('yt-dlp'),
        str(Path.home() / 'Library' / 'Python' / '3.9' / 'bin' / 'yt-dlp'),
        str(Path.home() / '.local' / 'bin' / 'yt-dlp'),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def is_url(text: str) -> bool:
    try:
        p = urlparse(text)
        return p.scheme in ('http', 'https') and bool(p.netloc)
    except Exception:
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source')
    p.add_argument('--output-dir', required=True)
    args = p.parse_args()

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    source = args.source

    if not is_url(source):
        src = Path(source).expanduser().resolve()
        if not src.exists():
            print(json.dumps({'status': 'error', 'message': f'file not found: {src}'}, ensure_ascii=False, indent=2))
            sys.exit(2)
        print(json.dumps({'status': 'ok', 'kind': 'local_file', 'source': str(src), 'video_path': str(src)}, ensure_ascii=False, indent=2))
        return

    ytdlp = find_ytdlp()
    if not ytdlp:
        print(json.dumps({'status': 'missing_dependency', 'message': 'yt-dlp not found. Install yt-dlp first.'}, ensure_ascii=False, indent=2))
        sys.exit(3)

    target_template = str(out_dir / 'source.%(ext)s')
    cmd = [
        ytdlp,
        '--no-playlist',
        '-o', target_template,
        '--print', 'after_move:filepath',
        source,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(json.dumps({'status': 'error', 'message': result.stderr.strip() or result.stdout.strip()}, ensure_ascii=False, indent=2))
        sys.exit(result.returncode)

    lines = [x.strip() for x in result.stdout.splitlines() if x.strip()]
    video_path = lines[-1] if lines else ''
    if not video_path or not Path(video_path).exists():
        print(json.dumps({'status': 'error', 'message': 'download finished but output file was not detected'}, ensure_ascii=False, indent=2))
        sys.exit(4)

    print(json.dumps({'status': 'ok', 'kind': 'remote_url', 'source': source, 'video_path': str(Path(video_path).resolve())}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
