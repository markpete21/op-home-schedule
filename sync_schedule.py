#!/usr/bin/env python3
"""Build games.json (public fields only) from a Microsoft 365 connector export of
'Basketball Schedule 26-27.xlsx'. Usage: python3 sync_schedule.py <export.txt>
Prints CHANGED or UNCHANGED. Never copies staffing, notes, VIP or other internal columns."""
import json, sys, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = "Home Games"
PUBLIC = {"date": "date", "time": "time", "home team": "home", "opponent": "opponent",
          "theme": "theme", "promotion/description": "description",
          "ticket url": "tickets", "stream url": "stream"}

def rows_of_sheet(text, name):
    m = re.search(r"^## Sheet:\s*" + re.escape(name) + r"\b.*$", text, re.M)
    if not m:
        sys.exit("ERROR: sheet '%s' not found in export" % name)
    body = text[m.end():]
    nxt = re.search(r"^## Sheet:", body, re.M)
    body = body[:nxt.start()] if nxt else body
    body = body.split("\nFormulas:")[0]
    return [l.split("\t") for l in body.splitlines() if l.strip() and not l.startswith("[")]

def main(path):
    rows = rows_of_sheet(open(path, encoding="utf-8").read(), SHEET)
    hi = next((i for i, r in enumerate(rows)
               if {"date", "opponent"} <= {c.strip().lower() for c in r}), None)
    if hi is None:
        sys.exit("ERROR: header row (Date / Opponent) not found")
    cols = [PUBLIC.get(c.strip().lower()) for c in rows[hi]]
    fallback = json.load(open(os.path.join(HERE, "descriptions.json"), encoding="utf-8"))
    games = []
    for r in rows[hi + 1:]:
        g = {}
        for i, k in enumerate(cols):
            if k and k not in g:
                g[k] = (r[i] if i < len(r) else "").strip()
        if not g.get("date") or not g.get("opponent") or not re.search(r"\d", g["date"]):
            continue
        if not g.get("description"):
            g["description"] = fallback.get((g.get("home", "") + "|" + g["opponent"]).lower(), "")
        games.append({k: v for k, v in g.items() if v})
    if not games:
        sys.exit("ERROR: no games parsed; leaving games.json untouched")
    out = os.path.join(HERE, "games.json")
    old = json.load(open(out)).get("games") if os.path.exists(out) else None
    if old == games:
        print("UNCHANGED (%d games)" % len(games)); return
    json.dump({"updated": datetime.datetime.now().astimezone().isoformat(timespec="minutes"),
               "source": "Home Games sheet", "games": games}, open(out, "w"), indent=1, ensure_ascii=False)
    print("CHANGED (%d games)" % len(games))

if __name__ == "__main__":
    main(sys.argv[1])
