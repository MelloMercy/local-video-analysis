#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def main():
    if len(sys.argv) != 2:
        print('usage: video_probe.py <video_path>', file=sys.stderr)
        sys.exit(1)
    video = Path(sys.argv[1]).expanduser().resolve()
    if not video.exists():
        print(f'file not found: {video}', file=sys.stderr)
        sys.exit(2)

    ffprobe = shutil.which('ffprobe')
    if ffprobe:
        out = run([
            ffprobe, '-v', 'error',
            '-show_entries', 'format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels',
            '-of', 'json', str(video)
        ])
        print(out.stdout.strip())
        return

    # macOS fallback via mdls
    out = run([
        'mdls',
        '-name', 'kMDItemDurationSeconds',
        '-name', 'kMDItemFSSize',
        '-name', 'kMDItemCodecs',
        '-name', 'kMDItemPixelHeight',
        '-name', 'kMDItemPixelWidth',
        str(video)
    ])
    lines = [x.strip() for x in out.stdout.splitlines() if x.strip()]
    data = {'path': str(video), 'fallback': 'mdls', 'raw': lines}
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
