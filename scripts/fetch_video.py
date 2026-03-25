#!/usr/bin/env python3
import argparse
import json
import re
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


def slugify(text: str, limit: int = 80) -> str:
    s = text.strip().lower()
    s = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff._-]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-._')
    return (s[:limit] or 'video').strip('-._')


def build_error(stderr: str, stdout: str) -> dict:
    raw = (stderr or stdout or '').strip()
    hint = None
    low = raw.lower()
    if 'login' in low or 'cookies' in low or 'sign in' in low:
        hint = 'The source may require cookies or login. Try --cookie-file or --cookies-from-browser.'
    elif 'drm' in low or 'protected' in low:
        hint = 'The source may be DRM-protected or otherwise restricted.'
    elif 'youtube' in low and ('reload' in low or 'signature extraction failed' in low):
        hint = 'The platform page is unstable right now. Retry later, or use cookies/browser login, or provide a direct media URL/local file.'
    return {'status': 'error', 'message': raw, 'hint': hint}


def read_info_json(path: Path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source')
    p.add_argument('--output-dir', required=True)
    p.add_argument('--cookie-file')
    p.add_argument('--cookies-from-browser', choices=['chrome', 'safari', 'firefox', 'edge', 'brave', 'chromium'])
    args = p.parse_args()

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    source = args.source

    if not is_url(source):
        src = Path(source).expanduser().resolve()
        if not src.exists():
            print(json.dumps({'status': 'error', 'message': f'file not found: {src}'}, ensure_ascii=False, indent=2))
            sys.exit(2)
        payload = {
            'status': 'ok',
            'kind': 'local_file',
            'source': str(src),
            'video_path': str(src),
            'source_host': None,
            'source_id': None,
            'suggested_run_name': src.stem,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    ytdlp = find_ytdlp()
    if not ytdlp:
        print(json.dumps({'status': 'missing_dependency', 'message': 'yt-dlp not found. Install yt-dlp first.'}, ensure_ascii=False, indent=2))
        sys.exit(3)

    parsed = urlparse(source)
    source_host = parsed.netloc.lower()
    target_template = str(out_dir / 'source.%(ext)s')
    info_json = out_dir / 'source.info.json'
    cmd = [
        ytdlp,
        '--no-playlist',
        '--write-info-json',
        '-o', target_template,
        '--print', 'after_move:filepath',
    ]
    if args.cookie_file:
        cmd.extend(['--cookies', str(Path(args.cookie_file).expanduser().resolve())])
    elif args.cookies_from_browser:
        cmd.extend(['--cookies-from-browser', args.cookies_from_browser])
    cmd.append(source)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(json.dumps(build_error(result.stderr, result.stdout), ensure_ascii=False, indent=2))
        sys.exit(result.returncode)

    lines = [x.strip() for x in result.stdout.splitlines() if x.strip()]
    video_path = lines[-1] if lines else ''
    if not video_path or not Path(video_path).exists():
        print(json.dumps({'status': 'error', 'message': 'download finished but output file was not detected'}, ensure_ascii=False, indent=2))
        sys.exit(4)

    info = read_info_json(info_json)
    source_id = info.get('id')
    title = info.get('title') or Path(video_path).stem
    title_slug = slugify(title, 60)
    id_slug = slugify(str(source_id), 20) if source_id else None
    if id_slug and id_slug != title_slug:
        suggested_run_name = f'{title_slug}-{id_slug}'
    else:
        suggested_run_name = title_slug

    payload = {
        'status': 'ok',
        'kind': 'remote_url',
        'source': source,
        'video_path': str(Path(video_path).resolve()),
        'info_json': str(info_json.resolve()) if info_json.exists() else None,
        'cookies_from_browser': args.cookies_from_browser,
        'cookie_file': str(Path(args.cookie_file).expanduser().resolve()) if args.cookie_file else None,
        'source_host': source_host,
        'source_id': source_id,
        'source_title': title,
        'suggested_run_name': suggested_run_name,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
