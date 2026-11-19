"""Find live streams about a topic, ranked by concurrent viewers.

usage: python streams.py --query "gta 6" --limit 20 --out streams.md
YouTube always. Twitch always (Helix if TWITCH_CLIENT_ID and TWITCH_TOKEN are set, else keyless public GQL). Kick is tried once, skipped silently on failure.
Viewer counts are exactly what the platform returned at run time.
"""
import argparse, json, os, sys, time
from pathlib import Path
from urllib.parse import quote_plus
sys.path.insert(0, str(Path(__file__).parent))
from common import ytdlp_base, run

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass


def fmt_dur(sec):
    if not sec or sec < 0:
        return ""
    sec = int(sec)
    return f"{sec // 3600}h{sec % 3600 // 60:02d}m"


def youtube(query, limit):
    """One flat search request. The search results already carry channel, title, live status,
    concurrent viewers and start time, so no per-video lookups (those hit YouTube's bot check
    from cloud and datacenter IPs)."""
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp=EgJAAQ%253D%253D"
    r = run(ytdlp_base() + ["--flat-playlist", "-J", "--playlist-end", str(limit), url], capture=True, check=False)
    if r.returncode != 0 or not r.stdout.strip():
        err = (r.stderr or "").strip().splitlines()
        print(f"WARNING: YouTube search failed, YouTube results are missing (not zero). "
              f"{err[-1][-300:] if err else 'no output from yt-dlp'}", file=sys.stderr)
        return None
    try:
        entries = [e for e in (json.loads(r.stdout).get("entries") or []) if e and e.get("id")]
    except ValueError as e:
        print(f"WARNING: YouTube search returned unreadable data, YouTube results are missing: {e}", file=sys.stderr)
        return None
    now = time.time(); out = []
    for e in entries:
        if e.get("live_status") not in (None, "is_live"):
            continue
        start = e.get("release_timestamp") or e.get("timestamp")
        out.append({"platform": "YouTube", "channel": e.get("channel") or e.get("uploader") or "",
                    "title": e.get("title") or "",
                    "url": e.get("url") or f"https://www.youtube.com/watch?v={e['id']}",
                    "viewers": e.get("concurrent_view_count"), "live_for": fmt_dur(now - start) if start else ""})
    if entries and all(x["viewers"] is None for x in out):
        print("WARNING: YouTube search returned streams but no viewer counts; the search page format may have "
              "changed. Update yt-dlp (pip install -U yt-dlp).", file=sys.stderr)
    return out


def twitch_nokey(game="Grand Theft Auto VI", limit=20):
    """No account/API key: Twitch public web GQL (see twitch.py)."""
    import twitch as tw
    try:
        rows = tw.top_streams(game, limit)
    except Exception as e:
        print(f"twitch (no key) failed: {e}", file=sys.stderr)
        return []
    now = time.time()
    return [{"platform": "Twitch", "channel": r["login"], "title": r["title"], "url": r["url"], "viewers": r["viewers"],
             "live_for": fmt_dur(now - tw.started_ts(r["created_at"])) if tw.started_ts(r["created_at"]) else ""} for r in rows]


def twitch(query):
    cid, tok = os.environ.get("TWITCH_CLIENT_ID"), os.environ.get("TWITCH_TOKEN")
    if not (cid and tok):
        return twitch_nokey()
    import requests
    h = {"Client-Id": cid, "Authorization": f"Bearer {tok}"}
    try:
        g = requests.get("https://api.twitch.tv/helix/games", params={"name": "Grand Theft Auto VI"}, headers=h, timeout=15).json()
        if not g.get("data"):
            return []
        gid = g["data"][0]["id"]
        s = requests.get("https://api.twitch.tv/helix/streams", params={"game_id": gid, "first": 100}, headers=h, timeout=15).json()
    except Exception as e:
        print(f"twitch failed: {e}", file=sys.stderr)
        return []
    now = time.time(); out = []
    for x in s.get("data", []):
        try:
            st = time.mktime(time.strptime(x["started_at"], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
        except Exception:
            st = None
        out.append({"platform": "Twitch", "channel": x.get("user_name", ""), "title": x.get("title", ""),
                    "url": f"https://twitch.tv/{x.get('user_login', '')}", "viewers": x.get("viewer_count"),
                    "live_for": fmt_dur(now - st) if st else ""})
    return out


def kick(query):
    """Public API is often blocked; one try, silent on any failure."""
    try:
        import requests
        r = requests.get("https://kick.com/api/v2/channels", params={"query": query}, timeout=8,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        data = r.json()
        items = data if isinstance(data, list) else data.get("data", [])
        return [{"platform": "Kick", "channel": c.get("slug", ""), "title": (c.get("livestream") or {}).get("session_title", ""),
                 "url": f"https://kick.com/{c.get('slug', '')}", "viewers": (c.get("livestream") or {}).get("viewer_count"),
                 "live_for": ""} for c in items if isinstance(c, dict) and c.get("livestream")]
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="gta 6"); ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--out", default="streams.md")
    a = ap.parse_args()
    y = youtube(a.query, a.limit)
    sections = [("YouTube", y)]
    t = twitch(a.query)
    if t:
        t = sorted(t, key=lambda r: r["viewers"] or -1, reverse=True)[:a.limit]
    if t is not None:
        sections.append(("Twitch", t))
    k = kick(a.query)
    if k:
        sections.append(("Kick", k))
    stamp = time.strftime("%Y-%m-%d %H:%M")
    md = [f"# Live streams: {a.query}", f"Checked {stamp}. Viewer counts are as returned at that moment.", ""]
    for name, rows in sections:
        md += [f"## {name}", ""]
        if rows is None:
            md += ["Lookup failed, see the warning in the terminal. This is not a count of zero.", ""]
            continue
        rows = sorted(rows, key=lambda r: r["viewers"] or -1, reverse=True)
        if not rows:
            md += ["No live streams found.", ""]
            continue
        md += ["| # | Channel | Title | Viewers | Live for | URL |", "|---|---|---|---|---|---|"]
        for n, r in enumerate(rows, 1):
            v = "" if r["viewers"] is None else r["viewers"]
            md.append(f"| {n} | {r['channel']} | {r['title'].replace('|', '/')} | {v} | {r['live_for']} | {r['url']} |")
            print(f"{name:8} {str(v):>7}  {r['channel'][:24]:24} {r['title'][:50]:50} {r['url']}")
        md.append("")
    Path(a.out).write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
