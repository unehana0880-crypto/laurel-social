"""Generate docs/index.html — the page GitHub Pages serves at the repo root.

It is a working index, not a landing page. It exists so you can:
  · confirm Pages is actually live (open it; if it loads, publishing will work)
  · click any card and see the exact URL Instagram will fetch
  · copy a Canva template URL to import into Canva

    python -m engine.build_index
"""
from __future__ import annotations
import html
from datetime import date
from . import config, render

DOCS = config.ROOT / "docs"
KIND = {"answer": ("Mon", "Answer"), "ritual": ("Wed", "Ritual"), "offer": ("Fri", "Offer")}


def build() -> str:
    biz = config.business()
    posts = config.queue()
    media = DOCS / "media"
    canva = sorted((DOCS / "canva").glob("*.html")) if (DOCS / "canva").exists() else []

    rows = []
    for i, p in enumerate(posts, 1):
        f = p.get("image") or render.media_filename(p)
        exists = (media / f).exists()
        d, label = KIND[p["kind"]]
        state = p["status"]
        rows.append(f'''<tr class="{state}">
  <td class="n">{i:02d}</td>
  <td class="dt">{p["date"]}<span>{d}</span></td>
  <td><span class="chip {p['kind']}">{label}</span></td>
  <td class="ti">{html.escape(p["card_title"])}</td>
  <td class="st">{state}</td>
  <td class="lk">{'<a href="media/'+html.escape(f)+'">open</a>' if exists else '<span class="miss">missing</span>'}</td>
</tr>''')

    tiles = "".join(
        f'<li><a href="canva/{c.name}">{c.stem}</a><code>canva/{c.name}</code></li>'
        for c in canva)

    counts = {k: sum(1 for p in posts if p["status"] == k)
              for k in ("pending", "published", "failed", "skipped")}
    have = sum(1 for p in posts if (media / (p.get("image") or render.media_filename(p))).exists())

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(biz["entity"]["name"])} — media index</title>
<style>
  :root{{--g:#F4F0E8;--c:#FAF8F3;--r:#EDE7DB;--h:rgba(45,44,40,.13);
    --i:#2D2C28;--d:#55534B;--f:#8A857A;--s:#6F8069;--o:#A8946F;
    --m:ui-monospace,SFMono-Regular,Menlo,monospace}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--g);color:var(--i);padding:0 20px 90px;
    font:400 15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif}}
  .w{{max-width:1000px;margin:0 auto}}
  header{{padding:52px 0 28px}}
  h1{{font:400 34px/1.1 Georgia,serif;letter-spacing:-.01em}}
  .sub{{color:var(--d);margin-top:12px;max-width:60ch}}
  .eyebrow{{font-family:var(--m);font-size:11px;letter-spacing:.22em;
    text-transform:uppercase;color:var(--s)}}
  h2{{font:400 22px/1.2 Georgia,serif;margin:44px 0 6px}}
  .note{{color:var(--f);font-size:13.5px;margin-bottom:16px}}
  .stats{{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}}
  .stat{{background:var(--c);border:1px solid var(--h);border-radius:2px;padding:10px 16px;
    font-family:var(--m);font-size:12px;color:var(--d)}}
  .stat b{{color:var(--i);font-weight:600}}
  .tw{{overflow-x:auto;border:1px solid var(--h);border-radius:2px;background:var(--c)}}
  table{{border-collapse:collapse;width:100%;min-width:660px;font-size:13.5px}}
  th{{font-family:var(--m);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--s);text-align:left;padding:11px 14px;background:var(--r);white-space:nowrap}}
  td{{padding:11px 14px;border-top:1px solid var(--h);vertical-align:middle}}
  tr.published{{opacity:.5}}
  .n,.st{{font-family:var(--m);font-size:11.5px;color:var(--f)}}
  .dt{{font-family:var(--m);font-size:12px;white-space:nowrap}}
  .dt span{{color:var(--f);margin-left:8px}}
  .ti{{color:var(--i)}}
  .chip{{font-family:var(--m);font-size:10.5px;letter-spacing:.08em;padding:3px 9px;
    border-radius:2px;border:1px solid var(--h);white-space:nowrap}}
  .chip.answer,.chip.offer{{background:var(--i);color:var(--g);border-color:var(--i)}}
  .chip.ritual{{background:var(--c);color:var(--s);border-color:rgba(111,128,105,.5)}}
  .lk a{{color:var(--s);font-family:var(--m);font-size:12px}}
  .miss{{color:#B4653F;font-family:var(--m);font-size:12px}}
  ul.kit{{list-style:none;display:grid;gap:1px;background:var(--h);
    border:1px solid var(--h);border-radius:2px}}
  ul.kit li{{background:var(--c);padding:13px 16px;display:flex;justify-content:space-between;
    align-items:center;gap:14px;flex-wrap:wrap}}
  ul.kit a{{color:var(--i);text-decoration:none;border-bottom:1px solid var(--s)}}
  ul.kit code{{font-family:var(--m);font-size:11.5px;color:var(--f)}}
  footer{{margin-top:52px;padding-top:22px;border-top:1px solid var(--h);
    color:var(--f);font-size:12.5px}}
</style></head><body><div class="w">
<header>
  <div class="eyebrow">{html.escape(biz["contact"]["instagram_handle"])} · media index</div>
  <h1>{html.escape(biz["entity"]["name"])}</h1>
  <p class="sub">If you can read this page, GitHub Pages is live and Instagram will be able to
  fetch the cards below. This page is the health check — nothing here is customer-facing.</p>
  <div class="stats">
    <div class="stat">cards on disk <b>{have}/{len(posts)}</b></div>
    <div class="stat">pending <b>{counts["pending"]}</b></div>
    <div class="stat">published <b>{counts["published"]}</b></div>
    <div class="stat">failed <b>{counts["failed"]}</b></div>
    <div class="stat">generated <b>{date.today().isoformat()}</b></div>
  </div>
</header>

<h2>Canva templates</h2>
<p class="note">Copy a link and give it to Claude to import into Canva, or paste it into
Canva's Import file dialog.</p>
<ul class="kit">{tiles or '<li><em>none built yet — run <code>python -m engine.canva_kit</code></em></li>'}</ul>

<h2>Scheduled cards</h2>
<p class="note">Every row is one post. <strong>open</strong> is the exact URL Instagram fetches —
if a link 404s, the publish for that day will skip rather than post a broken image.</p>
<div class="tw"><table>
<thead><tr><th></th><th>Date</th><th>Type</th><th>Title</th><th>Status</th><th>Image</th></tr></thead>
<tbody>
{"".join(rows)}
</tbody></table></div>

<footer>Regenerate with <code>python -m engine.build_index</code>. Cards render with
<code>python -m engine.render --to-docs</code>.</footer>
</div></body></html>
'''


if __name__ == "__main__":
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(build(), encoding="utf-8")
    (DOCS / ".nojekyll").touch()
    print("wrote docs/index.html")
