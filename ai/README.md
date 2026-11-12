# `ai/` — AI interaction logs and methods

CSAW AHA! requires that **every** interaction with generative AI be logged, and
that the Trojan and exploit be written *fully* by AI. These logs are the proof.
Missing or incomplete logs → disqualification.

## Files

| File | What it is |
|---|---|
| `interactions.jsonl` | **Source of truth.** One JSON object per AI interaction. Keep in git. |
| `AI_LOG.md` | Human-readable log for judges. **Auto-generated** — do not hand-edit. |
| `log_ai.py` | Adds entries and renders `AI_LOG.md`. |
| `portkey_logging.py` | Wrapper that auto-logs every Portkey/Gemini API call. |
| `transcripts/` | (optional) Full prompt/response text files for very long exchanges. |

## How we use AI (method · models · framework)

> Confirm/adjust these before submission — they must match the Technical Brief.

- **Method of interaction:** Portkey AI gateway (API), called from Python in a
  Jupyter notebook. Some exploratory steps used the Gemini web UI (logged by hand).
- **Model(s):** `vertexai/gemini-2.5-pro` via the NYU Portkey gateway.
- **Supporting framework:** **GHOST** one-shot insertion, extended by the
  **TrojanGYM** *detector-in-the-loop* agentic loop
  (generate → `iverilog` syntax check → functional testbench → **GNN4TJ/HW2VEC
  Trojan detector** → LLM-driven evasion retry). This agentic pipeline is the
  core of the "Creative Use of Generative AI" story.

## Logging discipline (so nothing gets missed)

1. **API calls:** route all model calls through `logged_chat()` in
   `portkey_logging.py`. Then every prompt/response is captured automatically.
2. **Chat-UI sessions done by hand:** immediately log them with
   `python log_ai.py add ...` (see `log_ai.py` header for the exact flags), or
   save the raw export under `transcripts/` and reference it.
3. After any batch of interactions: `python log_ai.py render` to refresh
   `AI_LOG.md`, then commit both `interactions.jsonl` and `AI_LOG.md`.

Each entry records: timestamp, actor, stage/role, interaction method, model,
framework, full prompt, full response, artifacts produced, and notes.

## What still needs backfilling

Experiment A (the AES T1 Trojan) and the reverse-engineering help were done
**before** this logger existed. Those prompts/responses live in the original
notebook run (`ghost_portkey_ai` export) and your chat histories — paste each
real exchange in via `log_ai.py add` so the record is complete. Do **not**
reconstruct from memory; use the actual transcripts.
