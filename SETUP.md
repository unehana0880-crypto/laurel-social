# Setup

Six steps. The only fiddly one is #4.

---

### 1 · Push it

```bash
git init && git add -A && git commit -m "laurel automation"
gh repo create laurel-social --private --source=. --push
```

Private is fine — Pages still serves `/docs` publicly, which is all Instagram needs.

The 36 cards are **already rendered and committed** under `docs/media`. That is
deliberate: because the images are live before any run fires, the weekly job
never has to render, commit, or wait for a Pages deploy. It just publishes.

### 2 · Turn on Pages

**Settings → Pages → Deploy from a branch → `main` / `/docs`**

Open `https://<you>.github.io/laurel-social/` when it builds. You should get the
media index — 36 rows, 6 Canva templates, `cards on disk 36/36`. Click any
**open** link; if the PNG loads, Instagram can fetch it too.

### 3 · Add the Pages URL as a variable

**Settings → Secrets and variables → Actions → Variables → New**

| Name | Value |
|---|---|
| `PAGES_BASE_URL` | `https://<you>.github.io/laurel-social` |

No trailing slash.

### 4 · Meta token

Instagram must be a **Business** account linked to a Facebook Page.

1. [developers.facebook.com](https://developers.facebook.com) → My Apps → Create App → **Business**
2. Add products: **Instagram Graph API** + **Facebook Login for Business**
3. Graph API Explorer → your app → request scopes:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
   `pages_read_engagement`, `pages_manage_posts`, `business_management`
4. Generate a user token, then exchange it for a long-lived one:

   ```
   GET /oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id=<APP_ID>
     &client_secret=<APP_SECRET>
     &fb_exchange_token=<SHORT_TOKEN>
   ```

5. `GET /me/accounts` with that long-lived user token. The `access_token` on your
   Page in the response is a **Page token that does not expire** — use that one,
   not the user token. Saving a short-lived token is the single most common way
   this breaks: it works when you test it and the cron dies an hour later.
6. Ids: `GET /me/accounts` → `FB_PAGE_ID`.
   `GET /<page-id>?fields=instagram_business_account` → `IG_USER_ID`.

**Settings → Secrets and variables → Actions → Secrets:**

| Secret | Value |
|---|---|
| `META_ACCESS_TOKEN` | the non-expiring Page token |
| `IG_USER_ID` | numeric |
| `FB_PAGE_ID` | numeric |

> Leave the app in **Development mode**. It can already post to Pages you
> administer, which is your case. App Review is only for posting on behalf of
> other people.

### 5 · Verify the token

```bash
IG_USER_ID=… FB_PAGE_ID=… META_ACCESS_TOKEN=… python -m engine.publish
```

Prints the account names, remaining publish quota, and the token's scopes.
`token_never_expires: true` is what you want to see.

### 6 · Dry run, then go

**Actions → Laurel Studio — auto publish → Run workflow**, `dry_run` **true**.
Prints the exact caption; publishes nothing.

Then run it again with `dry_run` **false** — one real post. Check both platforms.
After that the cron takes over: Mon/Wed/Fri 09:00 KST.

---

## Two fields still empty

`config/business.json` → `contact.booking_url` and `contact.facebook_page`.
Nothing blocks publishing without them, but the CTA reads better with a real link.

Optional, improves the schema: `whatsapp`, `telegram`, `google_maps_url`,
`naver_place_url`, `location.latitude` / `longitude`.

---

## Regenerating

```bash
python -m engine.plan --weeks 12 --force   # rebuild the schedule
python -m engine.render --to-docs          # re-render all cards into docs/media
python -m engine.canva_kit                 # rebuild the 6 Canva templates
python -m engine.build_index               # refresh docs/index.html
python -m engine.run --dry-run             # what would go out today
```

Change a price or a program name in `config/business.json`, run the middle three,
commit. Everything downstream follows.

## When a run does nothing

| Message | Meaning |
|---|---|
| `nothing scheduled for …` | not a Mon/Wed/Fri, or the row is already published |
| `… is not publicly reachable` | Pages is not serving `/docs`, or `PAGES_BASE_URL` is wrong |
| `docs/media/… is missing` | run `python -m engine.render --to-docs` and commit |
| `Invalid OAuth access token` | short-lived token saved — redo step 4.4 |
| `quota exhausted` | Instagram's rolling 24h cap; the run defers itself, nothing lost |
| `REFUSING TO PUBLISH` | a `TODO_` value is back in `config/business.json` |
| `banned word: 'warm'` | a temperature descriptor got into the copy — see `BRAND-RULES.md` |

Failures land in `content/log.jsonl` and the row is marked `failed`. Set it back
to `pending` and re-run with `catch_up`.
