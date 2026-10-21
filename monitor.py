#!/usr/bin/env python3
"""Free-games giveaway monitor. Prints NEW items as JSON lines; exits 0 always.
Usage: python3 monitor.py [--seed]"""
import json, urllib.request, re, sys, os, time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
LOG = os.path.join(HERE, "alerts_log.jsonl")

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
    return urllib.request.urlopen(req, timeout=30).read()

def norm(t):
    return re.sub(r"\s+", " ", t).strip().lower()

def fetch_reddit():
    out = []
    try:
        raw = get("https://www.reddit.com/r/FreeGamesOnSteam/new.rss").decode("utf-8", "replace")
        entries = re.findall(r"<entry>(.*?)</entry>", raw, re.S)
        for e in entries:
            title = norm(re.search(r"<title>(.*?)</title>", e, re.S).group(1))
            link = re.search(r'href="(https://www.reddit.com/r/FreeGamesOnSteam/comments/[^"]*)"', e)
            # strip reddit url params
            if link: link = link.group(1)
            out.append({"key": "r:" + title, "title": title, "link": link or "https://www.reddit.com/r/FreeGamesOnSteam/", "source": "reddit"})
    except Exception as e:
        out.append({"error": "reddit:" + type(e).__name__})
    return out

def fetch_epic():
    out = []
    try:
        data = json.loads(get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US"))
        for g in data["data"]["Catalog"]["searchStore"]["elements"]:
            promo = g.get("promotions") or {}
            slug = g.get("productSlug") or g.get("urlSlug") or ""
            url = "https://store.epicgames.com/en-US/p/" + slug if slug else "https://store.epicgames.com/en-US/free-games"
            for cat, label in [("promotionalOffers", "ACTIVE"), ("upcomingPromotionalOffers", "UPCOMING")]:
                for b in (promo.get(cat) or []):
                    for o in b.get("promotionalOffers", []):
                        if o.get("discountSetting", {}).get("discountPercentage") == 0:
                            end = o.get("endDate", "")[:10]
                            key = "e:" + norm(g["title"]) + ":" + o.get("startDate", "")[:10] + ":" + label
                            out.append({"key": key, "title": g["title"], "link": url, "source": "epic",
                                        "status": label, "free_until": end})
    except Exception as e:
        out.append({"error": "epic:" + type(e).__name__})
    return out

def main():
    seed = "--seed" in sys.argv
    state = {"seen": {}}
    if os.path.exists(STATE) and not seed:
        state = json.load(open(STATE))
    seen = state["seen"]
    items = fetch_reddit() + fetch_epic()
    new = []
    for it in items:
        if "error" in it:
            continue
        if it["key"] not in seen:
            seen[it["key"]] = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
            new.append(it)
    json.dump(state, open(STATE, "w"))
    for it in new:
        with open(LOG, "a") as f:
            f.write(json.dumps({**it, "found_at": seen[it["key"]]}) + "\n")
    print(json.dumps(new))

if __name__ == "__main__":
    main()
