# Brand rules — what the pipeline enforces

Everything here is checked automatically. A caption that violates any of it
fails at `stage` and never reaches the feed. This file is the human-readable
version of `config/brand.json → voice` and `config/business.json → compliance`.

## Banned words — enforced

**Temperature descriptors are banned brand-wide.** Seasonal counter-effect.

> heated · warm · warmth · cooling · cool · hot · chilled · toasty

Two sanctioned exceptions, and only these:

| Exception | Where it may appear |
|---|---|
| `warm heated bed` | The Décolleté & Body Care device only, for expectation management |
| `Ondol Floor` / `Traditional Ondol` | The floor. Never "heated floor", never "warm floor". |

Also banned: **spa** (we are a studio), transform, unlock, elevate, game-changer,
shocking.

## Claims — enforced

Never: cure · heal · treat acne · medical treatment · clinical results ·
permanent · removes wrinkles · whitening · chemical-free · toxin-free ·
blocks 100% · reflects UV

**full-body massage** is banned as a claim but permitted when negated — the
Décolleté & Body Care disclaimer says *"This is not a full-body massage"*, and
that sentence is required on every appearance of that program.

## Instagram — enforced

- **Maximum 5 hashtags.** Four fixed (`#seoultravel #koreaskincare #kbeauty #hongdae`) plus one contextual.
- Carousels: 3 sentences per slide maximum.
- Reels: everyday language only. No TEWL, stratum corneum, cytokines, fibroblasts.

## Voice — not machine-checkable, so read it

- Lead with the answer. Never withhold it as a hook.
- **Never use fear as a hook.** No "avoid this at all costs", no "stop doing this".
- **State the limitation of any evidence cited.** A null result or a small sample gets said out loud. This is also what makes an answer quotable by AI.
- If a claim cannot be traced to primary literature, leave it out.
- Understatement outperforms emphasis. No exclamation marks.
- Admitting we got something wrong is a feature. Write it plainly.
- Never use a discount as the primary message.
- Never write review text on a guest's behalf.

## Visual — set in config, not in code

`config/brand.json → active_palette`

| Value | Look |
|---|---|
| `daylight` **(active)** | Warm ivory ground, deep charcoal serif, soft sage and pale oak accents. Soft diffused daylight. Per the brand brief. |
| `obsidian` | The existing feed's black-and-gold. Preserved so the two can be compared or switched back. |

Change the one line, run `python -m engine.render`, and all 36 cards re-render
in the other palette. Nothing else needs touching.

Never show another brand's product logo. Never show an identifiable guest face.
