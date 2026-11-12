"""
portkey_logging.py  --  drop-in wrapper so EVERY Portkey call is logged.

The CSAW rule is that no hardware is written by a human and every AI interaction
is recorded. The safest way to satisfy that is to never call the model directly:
route all calls through logged_chat(), which records the prompt and response via
log_ai.log_interaction before returning.

Usage inside the TrojanGYM / GHOST notebook -- replace the raw get_llm_response
with a logged one:

    from portkey_logging import logged_chat

    def get_llm_response(prompt, *, stage="trojan-insertion",
                         actor="Yang", framework="TrojanGYM"):
        return logged_chat(prompt, stage=stage, actor=actor, framework=framework)

Every call then appends an entry to ai/interactions.jsonl automatically.
Set the model once via MODEL (or the PORTKEY_MODEL env var).
"""

import os

from log_ai import log_interaction

# Match whatever the notebook configures. vertexai/gemini-2.5-pro is what the
# team's Experiment A used; override with PORTKEY_MODEL if the config differs.
MODEL = os.environ.get("PORTKEY_MODEL", "vertexai/gemini-2.5-pro")
SYSTEM_PROMPT = (
    "You are an expert in hardware design and verification. "
    "Include ALL code from the input file in your response; you may only ADD "
    "code, never remove it. Do NOT stop generating after the first endmodule. "
    "Ensure ALL modules from the input are preserved. Do not truncate or use "
    'placeholder comments like "rest of code here".'
)


def logged_chat(prompt, *, stage, actor, framework="TrojanGYM",
                model=None, method="Portkey API", artifacts=None, notes="",
                client=None):
    """
    Send `prompt` to the configured Portkey model, log the exchange, return text.

    Pass an existing Portkey client via `client=` to reuse the notebook's
    configured one; otherwise a client is built from PORTKEY_API_KEY.
    """
    model = model or MODEL

    if client is None:
        from portkey_ai import Portkey
        api_key = os.environ.get("PORTKEY_API_KEY")
        if not api_key:
            raise RuntimeError("PORTKEY_API_KEY not set")
        client = Portkey(api_key=api_key)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    text = resp.choices[0].message.content or ""

    log_interaction(
        actor=actor,
        stage=stage,
        method=method,
        model=model,
        framework=framework,
        prompt=prompt,
        response=text,
        artifacts=artifacts or [],
        notes=notes,
    )
    return text
