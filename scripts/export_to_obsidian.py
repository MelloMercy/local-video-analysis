#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path


def slugify(text: str):
    safe = ''.join(c if c.isalnum() or c in '-_ .' else '-' for c in text)
    return '-'.join(safe.split()) or 'video-analysis'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-dir', required=True)
    p.add_argument('--vault-dir', required=True)
    p.add_argument('--subdir', default='Local Video Analysis')
    args = p.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    vault_dir = Path(args.vault_dir).expanduser().resolve()
    target_root = vault_dir / args.subdir / slugify(run_dir.name)
    target_root.mkdir(parents=True, exist_ok=True)

    wanted = [
        'report.final.md',
        'report.stub.md',
        'source_result.json',
        'probe.json',
        'transcript.clean.md',
        'transcript.timeline.md',
        'precise/precise_transcript.clean.md',
        'precise/precise_transcript.timeline.md',
        'precise/suspicious_segments.md',
    ]
    copied = []
    for rel in wanted:
        src = run_dir / rel
        if src.exists():
            dest = target_root / src.name
            shutil.copy2(src, dest)
            copied.append(str(dest))

    frames_dir = run_dir / 'frames'
    if frames_dir.exists():
        dest_frames = target_root / 'frames'
        if dest_frames.exists():
            shutil.rmtree(dest_frames)
        shutil.copytree(frames_dir, dest_frames)
        copied.append(str(dest_frames))

    print('\n'.join(copied))


if __name__ == '__main__':
    main()
