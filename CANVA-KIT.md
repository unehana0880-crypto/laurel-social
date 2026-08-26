# Canva kit — the manual half

The automated Mon/Wed/Fri posts never touch Canva; they render straight to PNG
and publish. Canva is for **Tuesday and Saturday** — the real photography, where
you need to place type over a picture by hand.

These templates exist so that manual half cannot drift from the automated half.
Same palette, same fonts, same margins, generated from the same `config/`.

```
docs/canva/overlay-diagnosis.html    1080×1350   photo + positioning line
docs/canva/overlay-founder.html      1080×1350   photo + Hana Kim's credentials
docs/canva/overlay-open.html         1080×1350   photo + today's open hours
docs/canva/reels-question.html       1080×1920   reels cover, 1:1 grid crop marked
docs/canva/reels-inside.html         1080×1920   reels cover, studio footage
docs/canva/menu-programs.html        A4 @300dpi  programs and pricing, print + screen
```

`out/kit/*.png` holds a flat preview of each.

---

## Getting them into Canva

Canva imports HTML as an **editable** design — text stays text, boxes stay
boxes. Each file is already annotated with `data-document-role="page"`, which is
what makes that work.

The importer needs a public HTTPS URL, and it must be a URL you already own —
never a file-sharing or pastebin service. Yours arrives as part of the normal
setup: **README step 2 puts this repo on GitHub Pages**, which serves `/docs`
publicly. Once that is live, each template sits at

```
https://<you>.github.io/<repo>/canva/menu-programs.html
```

and Claude can import all six into your Canva account in one pass. Ask for it
once Pages is up.

**Before Pages is live**, use Canva's own uploader: open Canva, **Create a
design → Import file**, and drag the `.html` file in from `docs/canva/`. Same
result, done by hand.

---

## Using them

**Photo overlays.** The `.photo` layer is a placeholder. Drop the real
photograph behind it and leave the scrim gradient in place — it is what keeps
ivory type legible over an unpredictable image. If a photo is very light, deepen
the scrim rather than darkening the type.

**Reels covers.** The dashed box marks the 1:1 area Instagram crops for the grid
thumbnail. Anything that has to survive in the grid belongs inside it. The area
above and below is seen only in the reels player.

**Menu.** A4 at 300 dpi, so it prints as-is. It is also the file to hand to the
booking page. Program names, prices and the body-care disclaimer all come from
`config/business.json` — change them there and re-run `python -m engine.canva_kit`
rather than editing the Canva copy, or the two will diverge.

---

## Rules that still apply here

Canva has no idea about your brand rules, so these are on you in the manual half:

- **No temperature words.** Not in the overlay text, not in the caption. `BRAND-RULES.md` has the full list and the two exceptions.
- **Maximum five hashtags.**
- **Never show another brand's product packaging or logo.**
- **Never show an identifiable guest face.**
- **No discount as the primary message.**

---

## Regenerating

```bash
python -m engine.canva_kit
```

Rebuilds all six from current config. The builder refuses to write a page whose
content overflows the canvas, so a caption that grew too long fails loudly
instead of shipping clipped.
