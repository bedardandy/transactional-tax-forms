#!/usr/bin/env python3
"""MCP server exposing the transactional-tax-forms library to agents.

Tools (stdio, FastMCP):
  find_forms(situation, top_k=5)        -> candidate tax forms (lexical router)
  get_form(form_id)                     -> metadata + mapping summary
  fill_form(form_id, case, out_path)    -> write a filled PDF, return {ok, path}
                                           + fill diagnostics; out_path may be
                                           a target .pdf filename or a directory

Run:      python3 tools/agent_server.py
Register: claude mcp add transactional-tax-forms -- python3 tools/agent_server.py

Requires ``mcp`` (pip install mcp). The import is lazy so the module documents
itself even without the dependency installed.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CATALOG = ROOT / "catalog"


def _index() -> list:
    return json.loads((CATALOG / "forms_index.json").read_text())["forms"]


def _route(situation: str, top_k: int) -> list:
    toks = set(re.findall(r"[a-z0-9]+", situation.lower()))
    scored = []
    for f in _index():
        hay = f"{f['form_id']} {f.get('title','')} {f.get('domain','')} {f.get('agency','')}".lower()
        htoks = set(re.findall(r"[a-z0-9]+", hay))
        score = len(toks & htoks)
        # light domain boost
        for d in ("corporation", "corporations", "estate", "probate", "real", "transfer", "withholding"):
            if d in toks and d[:6] in hay:
                score += 1
        if score:
            scored.append((score, f))
    scored.sort(key=lambda s: -s[0])
    return [{"form_id": f["form_id"], "title": f.get("title"), "domain": f.get("domain"),
             "status": f.get("status"), "score": s} for s, f in scored[:top_k]]


def _build():
    from mcp.server.fastmcp import FastMCP

    from engine.fill_via_mapping import fill_via_mapping

    mcp = FastMCP("transactional-tax-forms")

    @mcp.tool()
    def find_forms(situation: str, top_k: int = 5) -> list:
        """Route a free-text situation to candidate tax forms (corp / RE / probate)."""
        return _route(situation, top_k)

    @mcp.tool()
    def get_form(form_id: str) -> dict:
        """Return a form's metadata and a compact mapping summary."""
        d = ROOT / "forms" / form_id
        if not d.exists():
            return {"error": f"unknown form {form_id!r}"}
        meta = {f["form_id"]: f for f in _index()}.get(form_id, {})
        mp = {}
        if (d / "mapping.json").exists():
            mp = json.loads((d / "mapping.json").read_text())
        return {"form_id": form_id, "title": meta.get("title"), "domain": meta.get("domain"),
                "agency": meta.get("agency"), "status": meta.get("status"),
                "mapped_fields": len(mp.get("map", {}))}

    @mcp.tool()
    def fill_form(form_id: str, case: dict, out_path: str) -> dict:
        """Fill the form from a canonical case object; returns {ok, path} plus
        fill diagnostics (fields_written, unresolved keys, missing widgets)."""
        try:
            dest = pathlib.Path(out_path)
            if dest.suffix.lower() == ".pdf":
                out_dir = dest.parent  # honor the requested filename
            else:
                out_dir, dest = dest, None  # out_path is a directory
            r = fill_via_mapping(form_id, case, out_dir)
            path = r.get("out_pdf")
            if r.get("ok") and dest is not None and path and str(dest) != path:
                shutil.move(path, dest)
                path = str(dest)
            return {"ok": bool(r.get("ok")), "path": path,
                    "fields_written": r.get("fields_written"),
                    "unresolved": r.get("unresolved"),
                    "missing_widgets": r.get("missing_widgets"),
                    "overflowed": r.get("overflowed"),
                    "blank_verified": r.get("blank_verified"),
                    "status": r.get("status"),
                    "error": r.get("error")}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    return mcp


def main():
    try:
        mcp = _build()
    except ImportError:
        print("mcp not installed: pip install mcp", file=sys.stderr)
        return 1
    mcp.run()  # stdio transport
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
