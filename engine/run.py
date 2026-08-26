"""Weekly publisher — the entry point GitHub Actions calls.

All 36 cards are committed to docs/media at setup, so by the time a run fires the
image is already live on GitHub Pages. That removes the render → commit → wait →
publish dance entirely: a scheduled run only reads the queue, checks the image is
reachable, and calls Meta.

    python -m engine.run --dry-run     # print what would go out, publish nothing
    python -m engine.run               # publish today's post
    python -m engine.run --catch-up    # also publish anything overdue
"""
from __future__ import annotations
import argparse, json, os, sys, time
import urllib.request, urllib.error
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from . import config, copy as copybuilder, render, publish

KST = timezone(timedelta(hours=9))
DOCS = config.ROOT / "docs" / "media"
LOG = config.ROOT / "content" / "log.jsonl"


def _due(posts: list[dict], on: date, catch_up: bool) -> list[dict]:
    out = []
    for p in posts:
        if p["status"] != "pending":
            continue
        d = date.fromisoformat(p["date"])
        if d == on or (catch_up and d < on):
            out.append(p)
    return out


def _image_name(post: dict) -> str:
    """A row may point at its own photograph; otherwise use the rendered card."""
    return post.get("image") or render.media_filename(post)


def _public_url(fname: str) -> str:
    base = (os.environ.get("PAGES_BASE_URL") or "").rstrip("/")
    if not base:
        raise SystemExit(
            "PAGES_BASE_URL is not set.\n"
            "It must be the GitHub Pages root serving ./docs, e.g.\n"
            "  https://<you>.github.io/<repo>\n"
            "Instagram fetches the image itself and cannot read a private URL."
        )
    return f"{base}/media/{fname}"


def _reachable(url: str, tries: int = 3) -> bool:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(4 * (i + 1))
    return False


def _log(entry: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish scheduled posts")
    ap.add_argument("--dry-run", action="store_true", help="print everything, publish nothing")
    ap.add_argument("--catch-up", action="store_true", help="also publish overdue pending posts")
    ap.add_argument("--date", help="pretend today is YYYY-MM-DD")
    ap.add_argument("--max", type=int, default=2, help="ceiling on posts per run")
    a = ap.parse_args()

    today = date.fromisoformat(a.date) if a.date else datetime.now(KST).date()
    posts = config.queue()
    if not posts:
        print("queue is empty — run `python -m engine.plan`", file=sys.stderr)
        return 1

    batch = _due(posts, today, a.catch_up)[: a.max]
    if not batch:
        print(f"nothing scheduled for {today} — exiting clean")
        return 0

    todos = config.unresolved_todos()
    if todos and not a.dry_run:
        print("REFUSING TO PUBLISH — config/business.json still has placeholders:", file=sys.stderr)
        for t in todos:
            print(f"  · {t}", file=sys.stderr)
        return 2

    if not a.dry_run:
        left = publish.ig_quota_remaining()
        if left < len(batch):
            print(f"Instagram 24h quota exhausted ({left} left) — deferring", file=sys.stderr)
            return 0

    ok = 0
    for post in batch:
        built = copybuilder.build(post)
        banned = set(built["warnings"]) & set(config.business()["compliance"]["banned_claims"])
        if banned:
            print(f"  ! {post['id']} SKIPPED — banned claim: {sorted(banned)}", file=sys.stderr)
            continue
        for w in built["warnings"]:
            print(f"  ! {post['id']}: {w}", file=sys.stderr)

        fname = _image_name(post)
        local = DOCS / fname
        if not local.exists():
            print(f"  ! {post['id']} SKIPPED — {local.relative_to(config.ROOT)} is missing. "
                  f"Run `python -m engine.render --to-docs` and commit.", file=sys.stderr)
            continue

        if a.dry_run:
            print(f"\n{'='*72}\n[DRY RUN] {post['id']} · {post['date']} · {post['kind']}")
            print(f"image : docs/media/{fname}")
            print(f"alt   : {built['alt_text']}")
            print(f"{'-'*72}\n{built['caption']}\n{'='*72}")
            ok += 1
            continue

        url = _public_url(fname)
        if not _reachable(url):
            print(f"  ! {post['id']} SKIPPED — {url} is not publicly reachable. "
                  f"Is Pages serving /docs on the default branch?", file=sys.stderr)
            continue

        entry = {"id": post["id"], "date": post["date"], "kind": post["kind"],
                 "image": fname, "run_at": datetime.now(timezone.utc).isoformat()}
        try:
            if "instagram" in post["targets"]:
                entry["ig_media_id"] = publish.ig_publish(url, built["caption"])
            if "facebook" in post["targets"]:
                entry["fb_post_id"] = publish.fb_publish(local, built["caption"], built["alt_text"])
            post["status"] = "published"
            entry["status"] = "published"
            ok += 1
            print(f"  published {post['id']}  ig={entry.get('ig_media_id')}  fb={entry.get('fb_post_id')}")
        except publish.MetaError as e:
            post["status"] = "failed"
            entry["status"] = "failed"
            entry["error"] = str(e)
            print(f"  FAILED {post['id']}: {e}", file=sys.stderr)
        _log(entry)

    if not a.dry_run:
        config.save_queue(posts)

    print(f"\n{ok}/{len(batch)} handled for {today}")
    return 0 if ok == len(batch) else 1


if __name__ == "__main__":
    raise SystemExit(main())
