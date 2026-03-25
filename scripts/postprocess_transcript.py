#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

TERM_REPLACEMENTS = [
    (r'OpenCloud', 'OpenClaw'),
    (r'Open Cloud', 'OpenClaw'),
    (r'OpenClow', 'OpenClaw'),
    (r'多Engine', '多 Agent'),
    (r'Engine\'s', 'agents'),
    (r'Agent to Agent|Egent to Agent', 'agentToAgent'),
    (r'飞出|飞输|非书|Face to', 'Feishu'),
    (r'Apple Secret', 'App Secret'),
    (r'APP Secret', 'App Secret'),
    (r'APPID', 'App ID'),
    (r'Appid', 'App ID'),
    (r'AllowList', 'allowlist'),
    (r'AllowForm', 'allowFrom'),
    (r'Project Manager', 'project_manager'),
    (r'project manager', 'project_manager'),
    (r'全站工程师', '全栈工程师'),
    (r'全站开发工程师', '全栈工程师'),
    (r'绘画', '会话'),
    (r'Workspace', 'workspace'),
    (r'SenderMMONot in DMA list', 'sender ... not in DM allowlist'),
    (r'OpenClaw Gateway Restart|OpenCloud Gateway Restart', 'openclaw gateway restart'),
]


def normalize(text: str) -> str:
    out = text
    for pattern, repl in TERM_REPLACEMENTS:
        out = re.sub(pattern, repl, out)
    out = re.sub(r'\s+', ' ', out).strip()
    return out


def trim_repeated_tail(text: str) -> str:
    # remove highly repetitive tail sentences/phrases
    chunks = re.split(r'(?<=[。！？!?.])', text)
    if len(chunks) < 4:
        return text
    seen = {}
    cut = len(chunks)
    for i, c in enumerate(chunks):
        key = c.strip()
        if not key:
            continue
        seen[key] = seen.get(key, 0) + 1
        if i > len(chunks) * 0.7 and len(key) >= 6 and seen[key] >= 4:
            cut = min(cut, i)
            break
    text = ''.join(chunks[:cut]).strip()
    # trim repeated suffix window
    for size in [30, 24, 18, 12, 8]:
        if len(text) < size * 4:
            continue
        unit = text[-size:]
        reps = 1
        pos = len(text) - size * 2
        while pos >= 0 and text[pos:pos+size] == unit:
            reps += 1
            pos -= size
        if reps >= 4:
            text = text[:len(text) - size * reps + size].rstrip()
            break
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument('transcript_json')
    p.add_argument('--output-dir')
    args = p.parse_args()

    src = Path(args.transcript_json).expanduser().resolve()
    data = json.loads(src.read_text(encoding='utf-8'))
    out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    segments = data.get('segments', [])
    norm_segments = []
    for s in segments:
        t = normalize(s.get('text', '').strip())
        if not t:
            continue
        norm_segments.append({
            'start': s.get('start', 0),
            'end': s.get('end', 0),
            'text': t,
        })

    full = normalize(data.get('text', ''))
    full = trim_repeated_tail(full)

    # also stop when repeated phrase appears too many times at tail
    phrase = '我会变得更多的'
    idx = full.find(phrase * 2)
    if idx != -1:
        full = full[:idx].rstrip('，,。 .')

    clean_md = out_dir / 'transcript.post.clean.md'
    timeline_md = out_dir / 'transcript.post.timeline.md'
    txt = out_dir / 'transcript.post.txt'
    payload_path = out_dir / 'transcript.post.json'

    txt.write_text(full + '\n', encoding='utf-8')
    clean_md.write_text('# 转写清洁版（后处理增强）\n\n## 全文\n\n' + full + '\n', encoding='utf-8')

    lines = ['# 转写时间线版（后处理增强）', '']
    for s in norm_segments:
        start = int(float(s['start']))
        end = int(float(s['end']))
        sh, sm, ss = start // 3600, (start % 3600) // 60, start % 60
        eh, em, es = end // 3600, (end % 3600) // 60, end % 60
        lines += [f"## {sh:02d}:{sm:02d}:{ss:02d} - {eh:02d}:{em:02d}:{es:02d}", '', s['text'], '']
    timeline_md.write_text('\n'.join(lines), encoding='utf-8')

    out_payload = {'text': full, 'segments': norm_segments}
    payload_path.write_text(json.dumps(out_payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'ok', 'outputs': {'json': str(payload_path), 'txt': str(txt), 'clean_md': str(clean_md), 'timeline_md': str(timeline_md)}}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
