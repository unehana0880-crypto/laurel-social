# Laurel Studio — automated Instagram + Facebook publishing

Renders on-brand cards in the studio palette, writes answer-engine-optimised
English captions, and publishes to Instagram and Facebook three times a week
with no human in the loop.

```
Mon 09:00 KST   ANSWER   a real traveller question + a 40-60 word sourced answer   ← the AEO engine
Wed 09:00 KST   RITUAL   method and positioning — Ondol, the assessment, Hana Kim
Fri 09:00 KST   OFFER    a program, its price, how to book
Tue & Sat       — yours —  real studio photography, posted by hand
```

Every caption is checked against the brand rules before it can be staged —
banned temperature words, the five-hashtag cap, unhedged claims. See
`BRAND-RULES.md`.

Cost: **₩0/month.** GitHub Actions provides the scheduler, GitHub Pages hosts the
images, and the Meta Graph API is free.

---

## What is in here

```
BRAND-RULES.md            the enforced rules, in one page — read this first
CANVA-KIT.md              the Tue/Sat templates and how to import them
docs/canva/               six Canva-importable HTML templates
config/business.json      every fact about the studio — the single source of truth
config/brand.json         palettes, type, voice rules, banned words
content/pillars.json      24 AEO questions + 12 ritual pieces + 12 offers
content/queue.json        the generated schedule (editable by hand)
engine/                   plan → render → publish
aeo/                      JSON-LD schema, the AEO playbook, AI image prompts
docs/media/               rendered PNGs, served publicly by GitHub Pages
.github/workflows/        the Mon/Wed/Fri cron
```

---

## Setup

Roughly 90 minutes, once. Do it in this order — step 4 will not work before step 3.

### 1 · Finish `config/business.json`

Address, hours, programs, prices, founder and proof points are already filled in.
Nothing blocks publishing. Two fields are still worth adding before go-live:

- `contact.booking_url` — your booking page
- `contact.facebook_page`

Optional but valuable for schema completeness: `whatsapp`, `telegram`,
`google_maps_url`, `naver_place_url`, and `location.latitude` / `longitude`
(right-click your Google Maps pin, copy coordinates).

The pipeline refuses to publish if any `TODO_` value reappears, which is
deliberate — a caption naming the wrong address is worse than no caption.

### 2 · Put it on GitHub

```bash
git init && git add -A && git commit -m "Laurel Studio automation"
gh repo create laurel-social --private --source=. --push
```

A **private** repo is fine — GitHub Pages still serves `/docs` publicly, which is
all Instagram needs.

Then: **Settings → Pages → Source: Deploy from a branch → `main` / `/docs`.**
Wait for the first deploy, then confirm `https://<you>.github.io/laurel-social/`
loads. Add that URL as a repository **variable** named `PAGES_BASE_URL`
(Settings → Secrets and variables → Actions → Variables).

### 3 · Connect Meta

You need an Instagram **Business** account (not Creator, not Personal) linked to
a Facebook Page.

1. Instagram app → Settings → Account type → **switch to Business**, and link it to your Facebook Page.
2. [developers.facebook.com](https://developers.facebook.com) → **My Apps → Create App** → type **Business**.
3. Add the **Instagram Graph API** and **Facebook Login for Business** products.
4. Open **Graph API Explorer**, select your app, and request these permissions:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
   `pages_read_engagement`, `pages_manage_posts`, `business_management`
5. Generate a User token, then exchange it for a **long-lived Page token** —
   short-lived tokens expire in an hour and will break the cron:

   ```
   GET /oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id=<APP_ID>
     &client_secret=<APP_SECRET>
     &fb_exchange_token=<SHORT_LIVED_TOKEN>
   ```

   Then `GET /me/accounts` with that long-lived user token — the `access_token`
   on your Page in that response is a Page token that **does not expire**. Use
   that one.
6. Find your ids: `GET /me/accounts` returns `FB_PAGE_ID`.
   `GET /<page-id>?fields=instagram_business_account` returns `IG_USER_ID`.

Add three repository **secrets** (Settings → Secrets and variables → Actions):

| Secret | Value |
|---|---|
| `META_ACCESS_TOKEN` | the non-expiring Page token |
| `IG_USER_ID` | numeric Instagram business account id |
| `FB_PAGE_ID` | numeric Facebook Page id |

> While your app is in Development mode it can only post to Pages you administer
> — which is exactly your case, so **you do not need App Review.** Leave it in
> Development. Submitting for review is only needed to publish on behalf of
> other people's accounts.

### 4 · Dry run before you trust it

Actions tab → **Laurel Studio — auto publish** → **Run workflow** → leave
`dry_run` **true**.

It renders the cards, prints the exact captions, and publishes nothing. Download
the `rendered-cards` artifact and look at them. Read the captions properly — this
is the moment to catch a wrong price or an awkward line.

When you are happy, run it again with `dry_run` **false**. One real post goes out.
Check both platforms. Then leave the cron alone.

---

## Running it locally

```bash
pip install -r requirements.txt && python -m playwright install chromium

python -m engine.plan --weeks 12 --force   # rebuild the schedule
python -m engine.render --limit 6          # render to ./out, look at them
python -m engine.run --dry-run             # full pipeline, publishes nothing
python -m engine.publish                   # credential preflight only
```

---

## Everyday changes

**Rewrite a caption before it goes out** — edit the row in `content/queue.json`.
The publisher only reads rows with `"status": "pending"`.

**Skip a post** — set its `status` to `"skipped"`.

**Use a real photo instead of a rendered card** — drop the file in `docs/media/`
and put its filename in that row's `image` field.

**Add a question** — append to the `answer` array in `content/pillars.json`, then
`python -m engine.plan --weeks 12 --force`. Keep the capsule between 40 and 60
words, and state the limitation of any evidence you cite. Both are the mechanism,
not the polish; see the playbook.

**Change a price** — `config/business.json` only. It propagates to cards,
captions and schema. Never edit a price in a caption.

**Switch the whole look** — `config/brand.json → active_palette`. `daylight` is
the brief's muted natural palette; `obsidian` is the feed's original black and
gold. One line, then re-render.

---

## When it breaks

| Symptom | Cause |
|---|---|
| `REFUSING TO PUBLISH — placeholders` | `TODO` left in `config/business.json`. Working as intended. |
| `image never went live at …` | GitHub Pages not serving `/docs`, or `PAGES_BASE_URL` wrong |
| `container never became FINISHED` | Instagram could not fetch the image — the Pages URL is not publicly reachable |
| `(#10) requires instagram_content_publish` | permission missing from the token; regenerate it |
| `Invalid OAuth access token` | you saved a short-lived token — redo step 3.5 |
| `quota exhausted` | Instagram's rolling 24h publish cap. The run defers itself; nothing is lost. |
| Everything works, nothing appears | account is Creator or Personal, not Business |
| `banned word: 'warm'` | a temperature descriptor reached the copy — see `BRAND-RULES.md` |

Failures are logged to `content/log.jsonl` and the row is marked `"failed"` —
flip it back to `"pending"` and re-run with `catch_up`.

---

## The two posts that are still yours

Tuesday and Saturday are intentionally empty. This system produces the
consistent, factual, machine-readable half of the feed. It cannot photograph a
real guest's shoulders relaxing, and that is the half that actually converts.

Read `aeo/AEO-PLAYBOOK.md` before you write those — particularly §3, on why one
honest Reddit comment outperforms fifty posts.
