"""Build the publishing queue.

Mon = answer (AEO), Wed = ritual (brand), Fri = offer (conversion).
Tue/Sat are left empty on purpose — those are the two you post by hand.

The queue is a flat, human-editable list. Reorder it, delete a row, rewrite a
capsule — the publisher only ever reads the next row whose status is "pending".
"""
from __future__ import annotations
import argparse
from datetime import date, timedelta
from . import config

WEEKDAY = {"mon": 0, "wed": 2, "fri": 4}


def build(weeks: int = 12, start: date | None = None) -> list[dict]:
    ph = config.pillars()
    answers, rituals, offers = ph["answer"], ph["ritual"], ph["offer"]

    start = start or date.today()
    monday = start - timedelta(days=start.weekday())
    if monday < start:
        monday += timedelta(days=7)

    posts: list[dict] = []
    for w in range(weeks):
        base = monday + timedelta(weeks=w)
        for slot, pool, kind in (
            ("mon", answers, "answer"),
            ("wed", rituals, "ritual"),
            ("fri", offers, "offer"),
        ):
            item = dict(pool[w % len(pool)])
            if "card_title" not in item:  # offer rows are titled from the service
                s = config.service(item["service"])
                item["card_title"] = s["name"] if s else item["angle"]
            item.update(
                kind=kind,
                date=(base + timedelta(days=WEEKDAY[slot])).isoformat(),
                slot=slot,
                template=kind,
                status="pending",
                ai_image=False,
                image=None,
                targets=["instagram", "facebook"],
            )
            posts.append(item)
    return posts


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate content/queue.json")
    ap.add_argument("--weeks", type=int, default=12)
    ap.add_argument("--force", action="store_true", help="overwrite an existing queue")
    a = ap.parse_args()

    if config.queue() and not a.force:
        raise SystemExit("queue.json already exists — pass --force to rebuild (this discards edits)")

    posts = build(a.weeks)
    config.save_queue(posts)
    print(f"wrote {len(posts)} posts -> content/queue.json  ({a.weeks} weeks, 3/week)")

    todos = config.unresolved_todos()
    if todos:
        print(f"\n  {len(todos)} config placeholders still unresolved — publishing is blocked until these are filled:")
        for t in todos[:12]:
            print(f"   · {t}")
        if len(todos) > 12:
            print(f"   … and {len(todos) - 12} more")


if __name__ == "__main__":
    main()
