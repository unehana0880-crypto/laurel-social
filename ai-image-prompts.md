# AI image prompts — Laurel Studio

For Midjourney, CapCut AI or whichever generator you use. Drop the output into
`docs/media/` and point a queue row's `image` field at it, or use them for your
two manual posts each week.

**House style suffix** — append to every prompt:

```
warm ivory and pale oak palette with soft sage accents, deep charcoal shadows,
soft diffused daylight from a window out of frame, matte finish, shallow depth
of field, fine film grain, editorial stillness, 4:5 vertical, no text,
no watermark, no logo, no brand packaging
```

Set `--ar 4:5` (or 1080×1350) so it drops straight into the grid.

---

## Hard rules from the brand brief

- **Never show identifiable guest faces.** Hands, shoulders, the back of a neck, fabric, light on a wall.
- **Never show another brand's logo or packaging.** Unbranded vessels only. This is why the suffix ends with `no brand packaging`.
- **Never sexualize or objectify. Never feature minors.**
- **No temperature cues in the prompt or the caption** — no steam, no visible heat, no "cosy". Steam in particular reads as a temperature descriptor and is out.
- **No clinical or medical staging.** No gloves, no devices that read as medical, no treatment-room-as-surgery.

---

## Materials and objects

1. `An unbranded amber glass dropper bottle on pale oak, one drop suspended at the tip` + suffix
2. `Folded ivory cotton and linen cloths stacked on a wooden floor, seen at floor level` + suffix
3. `Macro of hanji paper texture, torn edge, sage-grey shadow, ivory ground` + suffix
4. `Dried mugwort and ginseng root arranged on pale oak, top-down, diffused daylight` + suffix
5. `A plain sheet mask folded like fabric on a wooden surface, one soft highlight along the fold` + suffix
6. `Still water in a shallow ceramic bowl, one ripple, seen from directly above` + suffix

## The space

7. `An empty maru room at floor level, low cushion, ivory walls, light entering from one side` + suffix
8. `A traditional Ondol floor seen from above with ivory bedding laid out, nobody in frame` + suffix
9. `Hanbok fabric draped over a wooden chair, sage and ivory tones, one shaft of daylight` + suffix
10. `A wooden window frame casting a soft grid of light onto a bare floor` + suffix

## Hands and gesture — no faces

11. `A single hand resting open on ivory linen, daylight raking across the knuckles` + suffix
12. `Two hands in the middle of folding a cloth, cropped at the wrists, ivory and oak` + suffix

---

## Where AI images should not be used

- Any treatment being performed — use real photography.
- Hana Kim, the therapists, the studio itself, or any guest.
- Before-and-after skin content of any kind.

Those are precisely what a prospective guest is evaluating, and a generated
version undermines the trust the rest of the system is built to earn. It also
sits badly next to a brand that states the limitations of its own evidence.

Every AI image posts with the disclosure line from `config/business.json →
compliance.ai_disclosure_line`.
