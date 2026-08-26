"""Single loader for every config file. Nothing else in the codebase opens JSON."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
CONTENT = ROOT / "content"
OUT = ROOT / "out"
ASSETS = ROOT / "assets"


def _load(p: Path) -> dict:
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def business() -> dict:
    return _load(CONFIG / "business.json")


def brand(kind: str | None = None) -> dict:
    """Resolves active_palette (and, for two-surface palettes, the surface this
    post type renders on) into a flat `palette` key, so the renderer never has to
    know which palette is live."""
    b = _load(CONFIG / "brand.json")
    pal = {k: v for k, v in b["palettes"][b["active_palette"]].items()
           if not k.startswith("_")}

    # A two-surface palette holds nested dicts ("dark"/"light") instead of colours.
    if pal and all(isinstance(v, dict) for v in pal.values()):
        surface = b.get("surface_by_kind", {}).get(kind or "", "dark")
        if surface not in pal:
            surface = next(iter(pal))
        pal = {k: v for k, v in pal[surface].items() if not k.startswith("_")}
        b["surface"] = surface
    else:
        b["surface"] = "single"

    b["palette"] = pal
    return b


def pillars() -> dict:
    return _load(CONTENT / "pillars.json")


def queue() -> list[dict]:
    p = CONTENT / "queue.json"
    return _load(p)["posts"] if p.exists() else []


def save_queue(posts: list[dict]) -> None:
    (CONTENT / "queue.json").write_text(
        json.dumps({"posts": posts}, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def service(sid: str) -> dict | None:
    for s in business()["services"]:
        if s["id"] == sid:
            return s
    return None


def unresolved_todos() -> list[str]:
    """Every TODO_ placeholder still sitting in config. Publishing is blocked while any remain."""
    found: list[str] = []

    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                if k.startswith("_"):
                    continue
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
        elif isinstance(node, str) and node.startswith("TODO"):
            found.append(f"{path} = {node}")

    walk(business())
    walk(pillars().get("hashtags", {}))
    return found
