"""Build the Canva template kit — the pieces you finish by hand on Tue/Sat.

Three templates, rendered from the same palette and fonts as the automated cards
so the manual half of the feed cannot drift from the automated half:

    overlay   1080x1350  text over a photograph
    reels     1080x1920  reels cover, with the 1:1 grid crop marked
    menu      1240x1754  A4 programs-and-pricing sheet, print and screen

Each is written twice:

    docs/canva/*.html   annotated with data-document-role="page" — the format
                        Canva's import-design-from-url turns into an editable
                        design, once the repo's GitHub Pages is live
    out/kit/*.png       flat previews you can look at right now

    python -m engine.canva_kit
"""
from __future__ import annotations
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright
from . import config

TPL = Path(__file__).parent / "templates"
ENV = Environment(loader=FileSystemLoader(str(TPL)), autoescape=select_autoescape(["html"]))
DOCS = config.ROOT / "docs" / "canva"
OUT = config.OUT / "kit"


def _specs(biz: dict) -> list[dict]:
    loc, ops = biz["location"], biz["operations"]
    where = f'{loc["floor"]}, {loc["street_address_en"]}'
    station = "Hongik Univ. Stn Exit 1 · 3 min"
    body = config.service("body")

    return [
        # ---------- photo overlays: one per recurring manual post type ----------
        dict(name="overlay-diagnosis", tpl="kit/overlay.html", w=1080, h=1350, kind="offer",
             variant="positioning", eyebrow="Laurel Studio", h1=86,
             headline="Not the treatment.\nThe diagnosis.",
             sub="Your skin is read before anything is applied. What it can tolerate today decides the rest.",
             meta="Hongdae, Seoul<br>English consultation"),
        dict(name="overlay-founder", tpl="kit/overlay.html", w=1080, h=1350, kind="offer",
             variant="founder", eyebrow="Who reads your skin", h1=74,
             headline="Hana Kim formulated\ningredients before\nshe applied them.",
             sub="Master's in bioengineering, Kumamoto University. 8,000+ recorded skin consultations.",
             meta="Founder<br>Laurel Studio"),
        dict(name="overlay-open", tpl="kit/overlay.html", w=1080, h=1350, kind="offer",
             variant="booking", eyebrow="Today", h1=92,
             headline="Hours still open\nthis afternoon.",
             sub="Treatments start on the hour, 10:00 to 19:00. Message us and we will tell you what is free.",
             meta=f'{ops["hours"]}<br>{station}'),

        # ---------- reels covers ----------
        dict(name="reels-question", tpl="kit/reels.html", w=1080, h=1920, kind="offer",
             variant="question", eyebrow="Questions you may have", h1=84,
             headline="Does mineral\nsunscreen really\nreflect UV?",
             sub="Mostly not. About 4–5% of it does.",
             handle=biz["contact"]["instagram_handle"]),
        dict(name="reels-inside", tpl="kit/reels.html", w=1080, h=1920, kind="offer",
             variant="studio", eyebrow="Inside the studio", h1=92,
             headline="Ninety seconds\nin the maru.",
             sub="Traditional Ondol floor. Hanbok. No fixed menu.",
             handle=biz["contact"]["instagram_handle"]),

        # ---------- menu ----------
        dict(name="menu-programs", tpl="kit/menu.html", w=1240, h=1754, kind="offer",
             tagline="Not the treatment. The diagnosis.",
             where=f'{where} · {station}',
             services=sorted(biz["services"], key=lambda s: s["code"]),
             note=body["important_disclaimer"],
             handle=biz["contact"]["instagram_handle"],
             hours=ops["hours"], station=station),
    ]


def build() -> tuple[list[Path], list[Path]]:
    biz = config.business()
    DOCS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    htmls, pngs = [], []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=os.environ.get("CHROMIUM_PATH") or None,
            args=["--force-color-profile=srgb", "--font-render-hinting=none"])

        for spec in _specs(biz):
            br = config.brand(spec["kind"])
            ctx = dict(spec)
            ctx.update(p=br["palette"], W=spec["w"], H=spec["h"],
                       fonts=(config.ASSETS / "fonts").resolve().as_uri())
            # Headlines carry deliberate line breaks; keep them as markup.
            for k in ("headline", "meta"):
                if k in ctx and isinstance(ctx[k], str):
                    ctx[k] = ctx[k].replace("\n", "<br>")
            html = ENV.get_template(spec["tpl"]).render(**ctx)

            hp = DOCS / f'{spec["name"]}.html'
            hp.write_text(html, encoding="utf-8")
            htmls.append(hp)

            page = browser.new_page(viewport={"width": spec["w"], "height": spec["h"]},
                                    device_scale_factor=2)
            page.goto(hp.as_uri())
            page.wait_for_timeout(300)

            over = page.evaluate(
                "() => { const el = document.querySelector('.page');"
                " return Math.max(0, el.scrollHeight - el.clientHeight); }")
            if over > 2:
                raise RuntimeError(
                    f'{spec["name"]}: content overflows the {spec["w"]}x{spec["h"]} page '
                    f'by {over}px — shorten the copy or reduce the type scale')

            pp = OUT / f'{spec["name"]}.png'
            page.screenshot(path=str(pp))
            page.close()
            pngs.append(pp)

        browser.close()
    return htmls, pngs


if __name__ == "__main__":
    h, p = build()
    for f in p:
        print(f"  {f.relative_to(config.ROOT)}")
    print(f"\n{len(p)} template(s). Editable HTML in docs/canva/ — import into Canva "
          f"with import-design-from-url once GitHub Pages is serving /docs.")
