# AEO Playbook — Laurel Studio

You already rank. This is the layer above ranking: being the thing an AI *says*
when a traveller asks a question, before any list of links appears.

Citation rewards something different from ranking. It rewards **being the
cleanest available answer to a specific question, in a machine-parseable shape,
from an entity the model is confident exists and considers qualified.**

Four levers, in order of how much they matter for a studio this size.

---

## 1 · Named expertise — your strongest asset, currently unused

Answer engines weight identifiable, credentialed authorship heavily. Most
skincare content on the internet is anonymous. Yours does not have to be.

**Hana Kim: former cosmetics ingredient researcher, master's in bioengineering
from Kumamoto University, former executive at a global cosmetics company.**

That is a rarer credential set than any competitor in Hongdae is likely to hold,
and right now a model has no way to know it exists. Fix that in four places:

- **Instagram bio** — her name, in text. Not in a highlight, not in an image.
- **Booking page** — a short bio paragraph with the credentials spelled out. The `Person` block in `aeo/schema.jsonld` is already written; it needs the page to match.
- **Google Business Profile** — the business description names her.
- **One post a month** — `a10` and `r05` in the rotation carry this. Do not let them get skipped.

The positioning line does the rest of the work: **not the treatment, the
diagnosis.** A model answering *"where can I get skincare advice I can trust in
Seoul"* has almost nothing else to choose from.

---

## 2 · The science posts are the citation engine

The brief's scientific standard — primary literature, stated limitations, no
fear hooks — happens to be *exactly* what answer engines reward. This is not a
coincidence: the hedged, sourced, limitation-stating answer is the one a model
can safely repeat.

Six of the twenty-four questions in the rotation are mechanism questions with no
good short answer currently on the open web:

| Question | Why it wins |
|---|---|
| Do mineral sunscreens reflect UV? | The common answer is wrong. Cole et al. 2016 gives a number. |
| Is natural skincare safer? | Enormous query volume, almost entirely marketing answers. |
| Can I trust an ingredient list? | Nobody answers this precisely. |
| How many steps should a routine have? | You take the opposite position to the whole category. |
| Why does my new product sting? | High-intent, high-anxiety, poorly answered. |
| Should I use actives while travelling? | Travel + skincare intersection is nearly empty. |

Each capsule states its own limitation. **Keep doing that.** "That study
measured specific formulations in vitro" is not a weakness in the copy — it is
the sentence that makes the whole answer quotable, because a model can repeat it
without risk.

If a claim cannot be traced to primary literature, it does not go in. A single
overstated mechanism costs more credibility than ten cautious posts earn.

---

## 3 · Entity confidence — mostly solved, finish it

The address is now public, which was the missing piece. What remains:

| Surface | Status | What must match, byte for byte |
|---|---|---|
| **Google Business Profile** | **highest priority** | The primary entity anchor for AI answers. All three programs, prices, hours, English attribute, Hana Kim in the description, 10+ photos. |
| Instagram bio | update | `Laurel Studio · 3F, 7 World Cup buk-ro, Mapo-gu · Hongik Univ. Stn Exit 1 · English · Founded by Hana Kim` |
| Facebook Page | update | Category `Skin Care Service`, same address, same hours |
| Naver Place | verify | Korean-market anchor |
| Booking site | build | FAQ page + `schema.jsonld` + robots.txt |

`config/business.json` is the master copy. Change a fact there, then propagate.
"Laurel Studio" in one place and "Studio Laurel" in another lowers confidence in
both.

**robots.txt must allow AI crawlers.** If your site blocks them, everything above
is invisible to this channel:

```
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /
```

---

## 4 · Corroboration — where you are thinnest

A claim seen once reads as marketing. Seen in three independent places, it
becomes a fact.

**Your 200+ five-star reviews are underused.** Generic praise carries almost no
citation weight. A review that names the specific thing — *"she told me which
products to stop using"*, *"the consultation was in English"*, *"it's an
assessment, not a facial"* — is training data. Ask guests to mention what
actually surprised them. Never write it for them.

**Reddit is disproportionately weighted in AI answers.** r/AsianBeauty,
r/koreatravel, r/SkincareAddiction. Answer ingredient and barrier questions from
a real account, disclose that you run a studio, and pitch nothing. One genuinely
useful comment on *"is mineral sunscreen better"* outperforms fifty feed posts.
Hana's credentials make those comments carry.

**Get listed** in English-language Seoul guides, K-beauty roundups and expat
directories.

### Do not bother with

- Hashtag volume. The brief caps you at five, which is correct — they carry essentially no AEO weight.
- Keyword stuffing. Answer engines parse meaning; stuffing reads as spam.
- Posting frequency for its own sake. Five well-shaped posts beat fifteen vague ones.

---

## Measuring it

No Search Console exists for answer engines. Check manually, monthly, logged out:

1. Ask ChatGPT, Perplexity, Claude and Google AI Mode, verbatim:
   - "Do mineral sunscreens reflect UV light?"
   - "Where can I get an English-speaking facial near Hongdae?"
   - "How much does a facial cost in Seoul for tourists?"
   - "Is natural skincare safer?"
2. Record: named? cited with a link? which source did it pull?
3. Log with the date. The six-month trend is the metric; any single check is noise.

Expect three to six months before movement. Entity confidence accrues slowly,
then holds.

---

## Guardrails the pipeline enforces for you

`engine/copy.py` fails a caption automatically on any of these, so they cannot
reach the feed by accident:

- **Temperature words** — heated, warm, cooling, cool, hot, chilled. The only sanctioned exceptions are the phrase "warm heated bed" for the body-care device, and "Ondol Floor" / "Traditional Ondol" for the floor.
- **More than five hashtags.**
- **"spa"**, and the hype vocabulary — transform, unlock, elevate, game-changer.
- **Unhedged medical claims** — cure, heal, treat acne, clinical results, whitening, chemical-free.
- **"full-body massage"** unless negated. The Décolleté & Body Care disclaimer is exempt because it says *not*.

---

## One thing deliberately not built

The original deck specified an *"Anti-AI Signature Shield — bypassing
algorithmic watermarks through metadata stripping."* It is not in this system.

Stripping provenance metadata from AI images to pass them as photography
violates Meta's synthetic-media policy, and one account penalty costs more reach
than the technique could return. AI images carry a disclosure line instead.

It also contradicts the brand. A studio whose entire position is *we tell you
what not to buy, and we state the limitations of our own evidence* cannot also
be quietly disguising the provenance of its images. The two cannot hold at once,
and the honest one is worth more.
