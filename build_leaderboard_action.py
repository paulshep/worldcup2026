#!/usr/bin/env python3
"""
Daily leaderboard + scores builder (GitHub Actions).
Primary source: API-Football (api-sports.io), key from env API_FOOTBALL_KEY (a GitHub
Actions secret \u2014 never stored in the repo). Fallback: openfootball public dataset.
Writes scores.json (consumed by the message-maker app) and rebuilds leaderboard.html.
Never blanks a populated page if a source is lagging.
"""
import json, urllib.request, urllib.error, datetime, sys, os, unicodedata

PLAYERS = [["Ali", ["Iran", "Japan"]], ["Carlotta", ["Cape Verde", "South Africa"]], ["Dan", ["Bosnia & Herzegovina", "Argentina"]], ["Elliot", ["Algeria", "France"]], ["Euan", ["Australia", "Colombia"]], ["George", ["Netherlands", "Ecuador"]], ["Hannah", ["Jordan", "Germany"]], ["Jack", ["Curaçao", "Saudi Arabia"]], ["Jan", ["Belgium", "Spain"]], ["Joseph", ["Tunisia", "Sweden"]], ["Josh", ["Uruguay", "Iraq"]], ["Jonathan", ["Ivory Coast", "Switzerland"]], ["Jenny", ["Croatia", "Egypt"]], ["Kate", ["USA", "Qatar"]], ["Katie", ["Paraguay", "Morocco"]], ["Laura", ["Uzbekistan", "Czech Republic"]], ["Lou", ["Mexico", "Brazil"]], ["Matt", ["Ghana", "Haiti"]], ["Mike", ["New Zealand", "Scotland"]], ["Nick", ["England", "South Korea"]], ["Patrick", ["Norway", "Senegal"]], ["Paul", ["Portugal", "Turkey"]], ["Sophie", ["Panama", "Austria"]], ["Vic", ["Canada", "DR Congo"]]]
FLAGS = {"Algeria": "🇩🇿", "Argentina": "🇦🇷", "Australia": "🇦🇺", "Austria": "🇦🇹", "Belgium": "🇧🇪", "Bosnia & Herzegovina": "🇧🇦", "Brazil": "🇧🇷", "Canada": "🇨🇦", "Cape Verde": "🇨🇻", "Colombia": "🇨🇴", "Croatia": "🇭🇷", "Curaçao": "🇨🇼", "Czech Republic": "🇨🇿", "DR Congo": "🇨🇩", "Ecuador": "🇪🇨", "Egypt": "🇪🇬", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "France": "🇫🇷", "Germany": "🇩🇪", "Ghana": "🇬🇭", "Haiti": "🇭🇹", "Iran": "🇮🇷", "Iraq": "🇮🇶", "Ivory Coast": "🇨🇮", "Japan": "🇯🇵", "Jordan": "🇯🇴", "Mexico": "🇲🇽", "Morocco": "🇲🇦", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Norway": "🇳🇴", "Panama": "🇵🇦", "Paraguay": "🇵🇾", "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Saudi Arabia": "🇸🇦", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸", "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Tunisia": "🇹🇳", "Turkey": "🇹🇷", "USA": "🇺🇸", "Uruguay": "🇺🇾", "Uzbekistan": "🇺🇿"}
T2P = {t: p for p, ts in PLAYERS for t in ts}
TEAM_OF = {p: ts for p, ts in PLAYERS}

# ---- team-name resolution (API spellings -> our canonical names) ----
def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return "".join(c for c in s.lower() if c.isalnum())

CANON = {norm(t): t for t in FLAGS}          # normalised -> our name
ALIAS = {
    "turkiye": "Turkey",
    "cotedivoire": "Ivory Coast",
    "congodr": "DR Congo", "democraticrepublicofcongo": "DR Congo",
    "democraticrepublicofthecongo": "DR Congo", "congokinshasa": "DR Congo",
    "unitedstates": "USA", "unitedstatesofamerica": "USA",
    "korearepublic": "South Korea", "koreasouth": "South Korea",
    "bosniaandherzegovina": "Bosnia & Herzegovina",
    "caboverde": "Cape Verde", "czechia": "Czech Republic",
}
_unmatched = set()
def resolve(name):
    n = norm(name)
    t = CANON.get(n) or ALIAS.get(n)
    # ignore knockout/group placeholders like 1A, 2B, W73, L101, 3A/B/C/D/F
    if not t and name and not name[0].isdigit() and not (name[0] in (chr(87),chr(76)) and name[1:].isdigit()):
        _unmatched.add(name)
    return t

# ---- primary: worldcup26.ir live API (keyless, real-time) ----
REZA_TEAMS = {"1": "Mexico", "2": "South Africa", "3": "South Korea", "4": "Czech Republic", "5": "Canada", "6": "Bosnia and Herzegovina", "7": "Qatar", "8": "Switzerland", "9": "Brazil", "10": "Morocco", "11": "Haiti", "12": "Scotland", "13": "United States", "14": "Paraguay", "15": "Australia", "16": "Turkey", "17": "Germany", "18": "Curaçao", "19": "Ivory Coast", "20": "Ecuador", "21": "Netherlands", "22": "Japan", "23": "Sweden", "24": "Tunisia", "25": "Belgium", "26": "Egypt", "27": "Iran", "28": "New Zealand", "29": "Spain", "30": "Cape Verde", "31": "Saudi Arabia", "32": "Uruguay", "33": "France", "34": "Senegal", "35": "Iraq", "36": "Norway", "37": "Argentina", "38": "Algeria", "39": "Austria", "40": "Jordan", "41": "Portugal", "42": "Democratic Republic of the Congo", "43": "Uzbekistan", "44": "Colombia", "45": "England", "46": "Croatia", "47": "Ghana", "48": "Panama"}
REZA_FIX = {"Turkiye":"Turkey","Cote d'Ivoire":"Ivory Coast"}  # safety, map already normalised
def fetch_live():
    url = "https://worldcup26.ir/get/games"
    req = urllib.request.Request(url, headers={"User-Agent": "wc26-bot", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.load(r)
    games = j if isinstance(j, list) else (j.get("data") or j.get("games") or j.get("matches") or [])
    out = []
    for g in games:
        a = REZA_TEAMS.get(str(g.get("home_team_id")))
        b = REZA_TEAMS.get(str(g.get("away_team_id")))
        a = resolve(a) if a else None
        b = resolve(b) if b else None
        if not a or not b:
            continue
        fin = str(g.get("finished")).upper() == "TRUE" or str(g.get("time_elapsed")).lower() in ("finished", "fulltime")
        try:
            gh = int(g.get("home_score")); ga = int(g.get("away_score"))
        except (TypeError, ValueError):
            continue
        if not fin:
            continue
        s2 = [gh, ga]
        for hk, ak in (("home_pens","away_pens"), ("home_penalties","away_penalties")):
            try:
                s2 += [int(g[hk]), int(g[ak])]; break
            except (KeyError, TypeError, ValueError):
                pass
        out.append({"a": a, "b": b, "s": s2})
    return out

# ---- fallback: openfootball ----
def fetch_openfootball():
    url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
    req = urllib.request.Request(url, headers={"User-Agent": "wc26-bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    out = []
    for m in data.get("matches", []):
        a = m.get("team1"); b = m.get("team2")
        if isinstance(a, dict): a = a.get("name")
        if isinstance(b, dict): b = b.get("name")
        a = resolve(a); b = resolve(b)
        if not a or not b: continue
        sc = m.get("score") or {}
        if not (sc.get("ft") or sc.get("et")): continue
        s = list(sc.get("et") or sc.get("ft"))
        if sc.get("ps"): s += list(sc["ps"])
        out.append({"a": a, "b": b, "s": s})
    return out

DIAG = {}
def get_matches():
    live, of = [], []
    try:
        live = fetch_live()
        DIAG["worldcup26"] = f"{len(live)} finished matches"
        print(f"worldcup26.ir: {len(live)} finished matches")
    except Exception as e:
        DIAG["worldcup26"] = "ERROR: " + str(e)[:200]
        print("worldcup26.ir failed:", e)
    try:
        of = fetch_openfootball()
        DIAG["openfootball"] = f"{len(of)} finished matches"
        print(f"openfootball: {len(of)} finished matches")
    except Exception as e:
        DIAG["openfootball"] = "ERROR: " + str(e)[:200]
        print("openfootball failed:", e)
    by_key = {}
    for m in of:   by_key[m["a"] + "|" + m["b"]] = m   # base
    for m in live: by_key[m["a"] + "|" + m["b"]] = m   # live wins
    merged = list(by_key.values())
    source = "worldcup26.ir" if live else ("openfootball" if of else "none")
    return merged, source

# ---- standings ----
def tally(matches):
    tbl = {p: {"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0} for p,_ in PLAYERS}
    played = 0
    for m in matches:
        a, b, s = m["a"], m["b"], m["s"]
        if not s: continue
        played += 1
        pens = s[2:4] if len(s) >= 4 else None
        for team, gf, ga, pd in ((a, s[0], s[1], (pens[0]-pens[1]) if pens else 0),
                                 (b, s[1], s[0], (pens[1]-pens[0]) if pens else 0)):
            p = T2P.get(team)
            if not p: continue
            r = tbl[p]; r["P"]+=1; r["GF"]+=gf; r["GA"]+=ga
            if gf>ga: r["W"]+=1
            elif gf<ga: r["L"]+=1
            elif pens:
                if pd>0: r["W"]+=1
                else: r["L"]+=1
            else: r["D"]+=1
    rows = []
    for p,_ in PLAYERS:
        r = tbl[p]; gd = r["GF"]-r["GA"]
        rows.append({"p":p, **r, "GD":gd, "Pts":r["W"]*3+r["D"], "teams":TEAM_OF[p]})
    rows.sort(key=lambda r: (-r["Pts"], -r["GD"], -r["GF"], r["p"]))
    return rows, played

def fl(a,b): return FLAGS.get(a,"") + FLAGS.get(b,"")
def gdstr(g): return ("+" if g>0 else "") + str(g)

def build_html(rows, played, css):
    if played == 0:
        sub = "The tournament is about to begin"; podium = ""; podium_style = ' style="display:none"'
        board = ('<div class="empty"><div class="big">No goals yet</div>'
                 '<p>The table wakes up the moment the first whistle blows. Check back after kick-off.</p></div>')
    else:
        leader = rows[0]
        sub = f'<b>{leader["p"]}</b> leads after <b>{played}</b> match{"" if played==1 else "es"} played'
        medals = {1:"\U0001F947", 2:"\U0001F948", 3:"\U0001F949"}
        def plinth(r, place):
            return (f'<div class="plinth p{place}"><div class="medal">{medals[place]}</div>'
                    f'<div class="nm">{r["p"]}</div><div class="pts">{r["Pts"]}</div>'
                    f'<div class="ptlabel">points</div><div class="teams">{fl(r["teams"][0],r["teams"][1])}</div>'
                    f'<div class="bar"></div></div>')
        t3 = rows[:3]; podium = plinth(t3[1],2) + plinth(t3[0],1) + plinth(t3[2],3); podium_style = ""
        body, pos, prev = [], 0, None
        for i, r in enumerate(rows):
            sig = (r["Pts"], r["GD"], r["GF"])
            if sig != prev: pos = i+1; prev = sig
            top = " top3" if pos <= 3 else ""
            gdcls = "pos" if r["GD"]>0 else ("neg" if r["GD"]<0 else "")
            body.append(
                f'<div class="row{top}"><div class="r-num">{pos}</div>'
                f'<div class="r-name">{r["p"]}<span class="flags">{fl(r["teams"][0],r["teams"][1])}</span></div>'
                f'<div class="r-pld">{r["P"]}</div>'
                f'<div class="r-wdl"><span class="w">{r["W"]}</span> {r["D"]} <span class="l">{r["L"]}</span></div>'
                f'<div class="r-gd {gdcls}">{gdstr(r["GD"])}</div>'
                f'<div class="r-pts">{r["Pts"]}</div></div>')
        board = ('<div class="thead"><div class="r-num">#</div><div>Player</div>'
                 '<div class="r-pld">Pl</div><div class="r-wdl">W&middot;D&middot;L</div>'
                 '<div class="r-gd">GD</div><div class="r-pts">Pts</div></div>' + "".join(body))
    updated = datetime.datetime.now(datetime.timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Sweepstake Standings &middot; World Cup 2026</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow"><span class="dot"></span> World Cup 2026</div>
  <h1>The <span class="accent">Sweepstake</span> Standings</h1>
  <div class="sub">{sub}</div>
  <div id="podium" class="podium"{podium_style}>{podium}</div>
  <div id="board" class="board">{board}</div>
  <div class="foot">
    <div class="legend">3 pts win &middot; 1 pt draw &middot; pens = win</div>
    <div class="refresh"><span id="stamp">Updated {updated} &middot; refreshed daily</span></div>
  </div>
</div>
</body>
</html>
"""

def main():
    css = open("leaderboard.css", encoding="utf-8").read()
    try:
        matches, source = get_matches()
    except Exception as e:
        print("all sources failed, leaving existing page:", e); return 0
    if _unmatched:
        print("WARNING unmatched team names:", sorted(_unmatched))
    rows, played = tally(matches)

    try:
        with open("build-status.json", "w", encoding="utf-8") as f:
            json.dump({"ran": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                       "diagnostics": DIAG, "played": played,
                       "unmatched": sorted(_unmatched)}, f, ensure_ascii=False, indent=1)
    except Exception as _e:
        print("could not write build-status.json:", _e)

    # anti-regression: don't blank a populated page on a lagging/empty source
    if played == 0 and os.path.exists("leaderboard.html"):
        if "No goals yet" not in open("leaderboard.html", encoding="utf-8").read():
            print("source empty but page already populated; keeping existing files"); return 0

    # write scores.json (keyed by our canonical names) for the message-maker app
    scores = {m["a"] + "|" + m["b"]: m["s"] for m in matches if m["s"]}
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                   "source": source, "scores": scores}, f, ensure_ascii=False)

    with open("leaderboard.html", "w", encoding="utf-8") as f:
        f.write(build_html(rows, played, css))
    print(f"rebuilt: {played} matches via {source}, leader {rows[0]['p'] if played else 'n/a'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
