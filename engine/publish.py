"""Meta Graph API publisher — Instagram feed + Facebook Page.

Instagram content publishing is a two-step flow: you POST a *container* that
references a publicly reachable image URL, then you POST that container's id to
media_publish. Meta's servers fetch the image themselves, which is why the PNG
has to live somewhere public first (see host.py — GitHub Pages by default).

Facebook is simpler: the Page photos edge accepts the bytes directly, and unlike
Instagram it accepts custom alt text, so accessibility text is set there.

Secrets come from the environment, never from a file:
    IG_USER_ID          Instagram *business* account id (numeric)
    FB_PAGE_ID          Facebook Page id (numeric)
    META_ACCESS_TOKEN   long-lived Page access token
    GRAPH_VERSION       optional, defaults below
"""
from __future__ import annotations
import os, time, json, argparse
from pathlib import Path
import urllib.request, urllib.parse, urllib.error

GRAPH_VERSION = os.environ.get("GRAPH_VERSION", "v21.0")
BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"


class MetaError(RuntimeError):
    pass


def _post(path: str, params: dict) -> dict:
    url = f"{BASE}/{path}"
    data = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise MetaError(f"{path} -> {e.code}: {e.read().decode()[:600]}") from None


def _get(path: str, params: dict) -> dict:
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise MetaError(f"{path} -> {e.code}: {e.read().decode()[:600]}") from None


def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise MetaError(f"missing environment variable {name}")
    return v


# --------------------------------------------------------------------------- IG

def ig_quota_remaining() -> int:
    """Instagram caps feed publishes per rolling 24h. Ask before spending."""
    r = _get(f"{_env('IG_USER_ID')}/content_publishing_limit",
             {"access_token": _env("META_ACCESS_TOKEN"), "fields": "config,quota_usage"})
    d = (r.get("data") or [{}])[0]
    cap = (d.get("config") or {}).get("quota_total", 50)
    return max(0, cap - d.get("quota_usage", 0))


def ig_publish(image_url: str, caption: str) -> str:
    ig, tok = _env("IG_USER_ID"), _env("META_ACCESS_TOKEN")

    container = _post(f"{ig}/media",
                      {"image_url": image_url, "caption": caption, "access_token": tok})
    cid = container["id"]

    # Meta downloads the image asynchronously; publishing early returns an error.
    for attempt in range(20):
        st = _get(cid, {"fields": "status_code,status", "access_token": tok})
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise MetaError(f"container {cid} failed: {st.get('status')}")
        time.sleep(min(3 + attempt, 12))
    else:
        raise MetaError(f"container {cid} never became FINISHED")

    return _post(f"{ig}/media_publish", {"creation_id": cid, "access_token": tok})["id"]


# --------------------------------------------------------------------------- FB

def fb_publish(image_path: Path, message: str, alt_text: str | None = None) -> str:
    """Multipart upload straight to the Page — no public URL needed."""
    page, tok = _env("FB_PAGE_ID"), _env("META_ACCESS_TOKEN")
    boundary = "----laurel" + str(int(time.time()))
    fields = {"message": message, "published": "true", "access_token": tok}
    if alt_text:
        fields["alt_text_custom"] = alt_text

    body = b""
    for k, v in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"; "
             f"filename=\"{image_path.name}\"\r\nContent-Type: image/png\r\n\r\n").encode()
    body += image_path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{BASE}/{page}/photos", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())["id"]
    except urllib.error.HTTPError as e:
        raise MetaError(f"fb photos -> {e.code}: {e.read().decode()[:600]}") from None


# --------------------------------------------------------------------------- check

def preflight() -> dict:
    """Verify credentials and permissions before a scheduled run depends on them."""
    tok = _env("META_ACCESS_TOKEN")
    out: dict = {}
    out["ig"] = _get(_env("IG_USER_ID"), {"fields": "id,username", "access_token": tok})
    out["fb"] = _get(_env("FB_PAGE_ID"), {"fields": "id,name", "access_token": tok})
    out["ig_quota_remaining"] = ig_quota_remaining()
    dbg = _get("debug_token", {"input_token": tok, "access_token": tok}).get("data", {})
    out["token_expires_at"] = dbg.get("expires_at")
    out["token_scopes"] = dbg.get("scopes")
    out["token_never_expires"] = dbg.get("expires_at") == 0
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Meta credential preflight")
    ap.parse_args()
    print(json.dumps(preflight(), indent=2))
