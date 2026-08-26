"""Caption construction.

The caption is the AEO asset, not the image. Answer engines index text.
Every caption follows one shape, and the shape is the strategy:

    line 1   the query, verbatim, as a question      -> matches what people type
    line 2-4 a 40-60 word answer capsule             -> the length AI lifts verbatim
    ---      three concrete facts                    -> structured data earns citation lift
    ---      one explicit call to action
    ---      the entity block, byte-identical every time
    ---      hashtags

The entity block repeating unchanged across hundreds of posts is what teaches an
answer engine that "Laurel Studio" is one place with one set of attributes.
Do not "vary it for freshness". Consistency is the point.
"""
from __future__ import annotations
import random
import re
from . import config

DIVIDER = "✦"


def _entity_block(biz: dict) -> str:
    """Byte-identical on every post. This repetition is the entity signal — do not vary it."""
    loc, ops = biz["location"], biz["operations"]
    return "\n".join([
        f"{biz['entity']['name']} · {loc['floor']}, {loc['street_address_en']}",
        f"{loc['nearest_station_ko']} Hongik Univ. Station · Open {ops['hours']} · English-speaking consultation",
    ])


def _price(s: dict) -> str:
    return f"${s['price_usd']} / ₩{s['price_krw']:,}"


def _hashtags(kind: str, ph: dict, br: dict, seed: int) -> str:
    """Brand brief caps Instagram at 5 tags, no exceptions. Four fixed + one contextual."""
    rnd = random.Random(seed)
    h = ph["hashtags"]
    cap = br["instagram"]["hashtag_max"]
    tags = list(h["core"]) + [rnd.choice(h["contextual"][kind])]
    return " ".join(tags[:cap])


def _banned_word_check(text: str, br: dict) -> list[str]:
    """Temperature descriptors are banned brand-wide. The body-care device and the
    Ondol floor are the only sanctioned exceptions, so allowed phrases are masked
    out of the text before the scan rather than special-cased per word."""
    bw = br["voice"]["banned_words"]
    scan = text.lower()
    for phrase in bw["exception_phrases"]:
        scan = scan.replace(phrase.lower(), " ")
    hits = []
    for w in bw["temperature"] + bw["other"]:
        if re.search(rf"\b{re.escape(w.lower())}\b", scan):
            hits.append(f"banned word: '{w}'")
    return hits


def _compliance_check(text: str, biz: dict) -> list[str]:
    """Banned phrases are banned as *claims*. A negation ("this is not a full-body
    massage") is the opposite of a claim and is exactly what we want said, so the
    check ignores any line that negates the phrase."""
    hits = []
    for w in biz["compliance"]["banned_claims"]:
        wl = w.lower()
        for line in text.splitlines():
            low = line.lower()
            if wl in low and not any(n in low for n in ("not a ", "not an ", "no ", "never ", "isn't", "is not")):
                hits.append(w)
                break
    return hits


def build(post: dict) -> dict:
    """post -> {caption, alt_text, warnings}"""
    biz, ph, br = config.business(), config.pillars(), config.brand()
    kind = post["kind"]
    seed = int(post["id"].lstrip("abcdefghijklmnopqrstuvwxyz") or 0) + hash(post["date"]) % 97

    cheapest = min(biz["services"], key=lambda s: s["price_usd"])
    hood = f"{biz['location']['neighborhood_public']}, {biz['location']['city']}"
    disclaimer = None

    if kind == "answer":
        head = post["query"]
        body = post["capsule"]
        facts = post["facts"]
        cta = (f"Programs from {_price(cheapest)}. Treatments on the hour, 10:00–19:00 — "
               f"same-day often available. Message us on WhatsApp, Telegram or DM.")
        alt = (f"Typographic card reading '{post['card_title']}' — {biz['entity']['name']}, "
               f"English-speaking K-beauty skincare studio in {hood}, founded by Hana Kim.")

    elif kind == "ritual":
        head = post["card_title"]
        body = post["line"]
        facts = biz["differentiators"][:3]
        cta = "Book on the hour, 10:00–19:00. Message us on WhatsApp, Telegram or DM."
        alt = (f"Editorial serif card reading '{post['card_title']}' — "
               f"{biz['entity']['name']}, personalized K-beauty skincare studio in {hood}.")

    else:  # offer
        svc = post.get("service")
        if svc == "all":
            head = "Three programs. Fixed prices."
            facts = [f"{s['name']} — {s['duration_min']} min — {_price(s)}" for s in
                     sorted(biz["services"], key=lambda s: s["code"])]
            alt = f"Price card listing the three K-beauty programs at {biz['entity']['name']} in {hood}."
        else:
            s = config.service(svc)
            head = f"{s['name']} — {s['duration_min']} minutes — {_price(s)}"
            facts = s["includes"][:4]
            disclaimer = s.get("important_disclaimer")
            alt = f"Card for {s['name']}, {s['duration_min']} minutes, at {biz['entity']['name']} in {hood}."
        body = post["line"]
        cta = f"{post['cta']} — same-day often available."

    parts = [head, "", body, "", *[f"{DIVIDER} {f}" for f in facts]]
    if disclaimer:
        # Expectation-setting outranks polish. This never gets trimmed for length.
        parts += ["", f"Please note: {disclaimer}"]
    parts += ["", cta, "", _entity_block(biz), "", _hashtags(kind, ph, br, seed)]
    caption = "\n".join(parts)

    if post.get("ai_image"):
        caption = caption.replace(cta, cta + f"\n\n{biz['compliance']['ai_disclosure_line']}")

    warnings = _compliance_check(caption, biz) + _banned_word_check(caption, br)
    if len(caption) > 2200:
        warnings.append(f"caption is {len(caption)} chars — Instagram truncates at 2200")

    return {"caption": caption, "alt_text": alt[:990], "warnings": warnings}
