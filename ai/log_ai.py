#!/usr/bin/env python3
"""
log_ai.py  --  AI-interaction logger for the CSAW AHA! challenge.

Every use of generative AI in this project must be recorded (CSAW rule:
missing/incomplete AI logs => disqualification). This tool keeps the record
in ONE machine-readable file (interactions.jsonl, one JSON object per line)
and renders a human-readable AI_LOG.md from it for the judges.

Two ways to add an entry:

1. From Python (preferred -- automatic, nothing gets missed):

       from log_ai import log_interaction
       log_interaction(
           actor="Yang",
           stage="trojan-insertion",
           method="Portkey API",
           model="vertexai/gemini-2.5-pro",
           framework="GHOST",
           prompt=prompt_text,
           response=response_text,
           artifacts=["experiment_a/trojan_aes.v"],
           notes="initial T1 insertion into AES-128",
       )

   (portkey_logging.py wraps the Portkey client so this happens on its own.)

2. From the command line (for chat-UI sessions you did by hand):

       python log_ai.py add \
         --actor Mitsuki --stage reverse-engineering \
         --method "web UI (Gemini)" --model gemini-2.5-pro --framework none \
         --prompt-file prompt.txt --response-file reply.txt \
         --notes "asked it to explain the recovered netlist"

Then regenerate the readable log:

       python log_ai.py render

interactions.jsonl is the source of truth -- keep it in git. Long prompts or
responses may be stored as separate files under ai/transcripts/ and referenced
by path instead of pasted inline; pass --prompt-file / --response-file for that.
"""

import argparse
import datetime as _dt
import json
import os
from pathlib import Path

AI_DIR = Path(__file__).resolve().parent
JSONL_PATH = AI_DIR / "interactions.jsonl"
MD_PATH = AI_DIR / "AI_LOG.md"

FIELDS = [
    "id", "timestamp", "actor", "stage", "method",
    "model", "framework", "prompt", "response", "artifacts", "notes",
]


def _now():
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _read_all():
    if not JSONL_PATH.exists():
        return []
    rows = []
    for line in JSONL_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _next_id(rows):
    return (max((r.get("id", 0) for r in rows), default=0) + 1)


def log_interaction(actor, stage, method, model, framework,
                    prompt, response, artifacts=None, notes="", timestamp=None):
    """Append one interaction. Returns the stored record."""
    rows = _read_all()
    rec = {
        "id": _next_id(rows),
        "timestamp": timestamp or _now(),
        "actor": actor,
        "stage": stage,
        "method": method,
        "model": model,
        "framework": framework,
        "prompt": prompt,
        "response": response,
        "artifacts": list(artifacts or []),
        "notes": notes,
    }
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def _maybe_file(text, file_path):
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    return text or ""


def cmd_add(args):
    rec = log_interaction(
        actor=args.actor,
        stage=args.stage,
        method=args.method,
        model=args.model,
        framework=args.framework,
        prompt=_maybe_file(args.prompt, args.prompt_file),
        response=_maybe_file(args.response, args.response_file),
        artifacts=args.artifact or [],
        notes=args.notes or "",
    )
    print(f"logged interaction #{rec['id']} ({rec['stage']}, {rec['model']})")
    cmd_render(args, quiet=True)


def _trunc(text, limit=6000):
    text = text or ""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n...[truncated {len(text) - limit} chars; full text in interactions.jsonl]..."


def cmd_render(args, quiet=False):
    rows = _read_all()
    lines = []
    w = lines.append
    w("# AI Interaction Log")
    w("")
    w("_Auto-generated from `interactions.jsonl` by `log_ai.py`. "
      "Do not edit by hand -- edit the JSONL and re-run `python log_ai.py render`._")
    w("")
    w(f"Total logged interactions: **{len(rows)}**")
    w("")

    # Summary tables (judge-friendly: shows the pipeline at a glance).
    def _counts(key):
        c = {}
        for r in rows:
            c[r.get(key, "?")] = c.get(r.get(key, "?"), 0) + 1
        return dict(sorted(c.items(), key=lambda kv: -kv[1]))

    if rows:
        w("## Summary")
        w("")
        w("| By model | count |")
        w("|---|---|")
        for k, v in _counts("model").items():
            w(f"| `{k}` | {v} |")
        w("")
        w("| By stage/role | count |")
        w("|---|---|")
        for k, v in _counts("stage").items():
            w(f"| {k} | {v} |")
        w("")

    w("## Interactions")
    w("")
    for r in rows:
        w(f"### #{r['id']} -- {r.get('stage','?')} "
          f"({r.get('timestamp','?')})")
        w("")
        w(f"- **Actor:** {r.get('actor','?')}")
        w(f"- **Method:** {r.get('method','?')}")
        w(f"- **Model:** `{r.get('model','?')}`")
        w(f"- **Framework:** {r.get('framework','?')}")
        if r.get("artifacts"):
            w(f"- **Artifacts produced:** {', '.join('`'+a+'`' for a in r['artifacts'])}")
        if r.get("notes"):
            w(f"- **Notes:** {r['notes']}")
        w("")
        w("**Prompt:**")
        w("")
        w("```text")
        w(_trunc(r.get("prompt", "")))
        w("```")
        w("")
        w("**AI response:**")
        w("")
        w("```text")
        w(_trunc(r.get("response", "")))
        w("```")
        w("")
        w("---")
        w("")

    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    if not quiet:
        print(f"wrote {MD_PATH} ({len(rows)} interactions)")


def main():
    p = argparse.ArgumentParser(description="AI-interaction logger")
    sub = p.add_subparsers(required=True)

    a = sub.add_parser("add", help="append one interaction")
    a.add_argument("--actor", required=True)
    a.add_argument("--stage", required=True,
                   help="e.g. trojan-insertion, syntax-repair, testbench-repair, "
                        "evasion, reverse-engineering, brief-writing")
    a.add_argument("--method", required=True, help='e.g. "Portkey API", "web UI (Gemini)"')
    a.add_argument("--model", required=True, help="e.g. vertexai/gemini-2.5-pro")
    a.add_argument("--framework", default="none", help="e.g. GHOST, TrojanGYM, none")
    a.add_argument("--prompt", default="")
    a.add_argument("--prompt-file", default="")
    a.add_argument("--response", default="")
    a.add_argument("--response-file", default="")
    a.add_argument("--artifact", action="append", help="repeatable; file produced")
    a.add_argument("--notes", default="")
    a.set_defaults(func=cmd_add)

    r = sub.add_parser("render", help="regenerate AI_LOG.md from interactions.jsonl")
    r.set_defaults(func=cmd_render)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
