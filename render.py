"""HTML -> PNG at 1080x1350 via headless Chromium.

Type sizes auto-fit: long questions step the headline down rather than overflowing
the canvas. Nothing is ever allowed to clip — a clipped card is a failed render.
"""
from __future__ import annotations
import argparse, os, re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright
from . import config

TPL = Path(__file__).parent / "templates"
ENV = Environment(loader=FileSystemLoader(str(TPL)), autoescape=select_autoescape(["html"]))


def _fit(text: str, big: int, small: int, lo: int = 34, hi: int = 92) -> int:
    """Step headline size down as character count climbs."""
    n = len(text)
    if n <= lo:
        return big
    if n >= hi:
        return small
    return round(big + (small - big) * (n - lo) / (hi - lo))


def _ctx(post: dict, biz: dict, br: dict) -> tuple[str, dict]:
    p, cv = br["palette"], br["canvas"]["feed"]
    kind = post["kind"]

    base = dict(
        p=p, W=cv["w"], H=cv["h"],
        margin=br["canvas"]["safe_margin_px"],
        orn_opacity=br["ornament"]["opacity"] if br["ornament"]["enabled"] else 0,
        fonts=(config.ASSETS / "fonts").resolve().as_uri(),
        brand_name=biz["entity"]["name"],
        handle=biz["contact"]["instagram_handle"],
        extra_class="", measure=790, quote=76, lede_px=27, h1=72,
        facts=None, rows=None, sub=None, lede="",
        price=None, price_krw=None, duration=None, note=None,
    )

    if kind == "answer":
        title = post["card_title"]
        base.update(
            eyebrow="Questions you may have",
            title=title,
            h1=_fit(title, 74, 50),
            lede=post["capsule"],
            facts=post["facts"],
            foot_right="English consultation",
        )
        return "answer.html", base

    if kind == "ritual":
        title = post["card_title"]
        base.update(
            eyebrow='The Ritual',
            title=title,
            quote=_fit(title, 88, 58),
            h1=_fit(title, 88, 58),
            lede=post["line"],
            sub=post.get("sub"),
            measure=840,
            foot_right="Barrier first",
        )
        return "ritual.html", base

    # offer
    svc = post.get("service")
    if svc == "all":
        base.update(
            eyebrow='Programs <span class="thin">&nbsp;·&nbsp; Fixed pricing</span>',
            title="Choose your care.",
            h1=64, lede=post["line"],
            rows=sorted(biz["services"], key=lambda s: s["code"]),
            foot_right=post["cta"],
        )
    else:
        s = config.service(svc)
        base.update(
            eyebrow=f'Program {s["code"]}',
            title=s["name"],
            h1=_fit(s["name"], 76, 54),
            price=s["price_usd"],
            price_krw=f'₩{s["price_krw"]:,}',
            duration=s["duration_min"],
            lede=post["line"],
            facts=s["includes"][:4],
            note=s.get("important_disclaimer"),
            measure=760,
            foot_right=post["cta"],
        )
    return "offer.html", base


def media_filename(post: dict) -> str:
    """The one place a card's filename is decided. The publisher derives the
    public URL from this, so renderer and publisher can never disagree."""
    slug = re.sub(r"[^a-z0-9]+", "-", post["card_title"].lower()).strip("-")[:48]
    return f'{post["date"]}_{post["id"]}_{slug}.png'


def render_one(post: dict, page, biz: dict, br: dict, outdir: Path) -> Path:
    br = config.brand(post["kind"])   # two-surface palettes vary by post type
    tpl_name, ctx = _ctx(post, biz, br)
    html = ENV.get_template(tpl_name).render(**ctx)

    tmp = outdir / f".{post['id']}.html"
    tmp.write_text(html, encoding="utf-8")
    page.goto(tmp.as_uri())
    page.wait_for_timeout(260)  # font settle

    overflow = page.evaluate(
        "() => { const s=document.querySelector('.sheet');"
        "return s.scrollHeight - s.clientHeight; }"
    )
    if overflow > 2:
        raise RuntimeError(f"{post['id']}: content overflows canvas by {overflow}px — shorten the copy")

    out = outdir / media_filename(post)
    page.screenshot(path=str(out))
    tmp.unlink(missing_ok=True)
    return out


def render_many(posts: list[dict], outdir: Path | None = None,
                scale: int | None = None) -> list[Path]:
    biz, br = config.business(), config.brand()
    outdir = outdir or config.OUT
    outdir.mkdir(parents=True, exist_ok=True)
    cv = br["canvas"]["feed"]

    made = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=os.environ.get("CHROMIUM_PATH") or None,
            args=["--force-color-profile=srgb", "--font-render-hinting=none"],
        )
        page = browser.new_page(
            viewport={"width": cv["w"], "height": cv["h"]},
            device_scale_factor=scale or br["canvas"]["scale"],
        )
        for post in posts:
            made.append(render_one(post, page, biz, br, outdir))
        browser.close()
    return made


def main() -> None:
    ap = argparse.ArgumentParser(description="Render queued posts to PNG")
    ap.add_argument("--limit", type=int, default=0, help="0 = all pending")
    ap.add_argument("--all", action="store_true", help="include already-published rows")
    ap.add_argument("--to-docs", action="store_true",
                    help="render into docs/media (the folder GitHub Pages serves)")
    a = ap.parse_args()

    posts = config.queue()
    if not a.all:
        posts = [p for p in posts if p["status"] == "pending"]
    if a.limit:
        posts = posts[: a.limit]
    if not posts:
        raise SystemExit("nothing to render — run `python -m engine.plan` first")

    # Instagram serves feed images at 1080px wide, so cards bound for the repo
    # render at 1x. Keeps the committed folder near 18 MB instead of 46 MB.
    dest = (config.ROOT / "docs" / "media") if a.to_docs else None
    for f in render_many(posts, dest, scale=1 if a.to_docs else None):
        print(f"  {f.relative_to(config.ROOT)}")
    print(f"\nrendered {len(posts)} card(s) at "
          f"{config.brand()['canvas']['feed']['w']}x{config.brand()['canvas']['feed']['h']} "
          f"@{config.brand()['canvas']['scale']}x")


if __name__ == "__main__":
    main()
