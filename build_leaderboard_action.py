#!/usr/bin/env python3
"""
Daily static leaderboard builder for the family World Cup 2026 sweepstake.
Runs in GitHub Actions on a schedule. Fetches scores from the openfootball
dataset (public domain, updated ~once a day) and regenerates leaderboard.html.
No API key required. If the fetch fails, the existing leaderboard.html is left as-is.
"""
import json, urllib.request, datetime, sys, os

PLAYERS = [["Ali", ["Iran", "Japan"]], ["Carlotta", ["Cape Verde", "South Africa"]], ["Dan", ["Bosnia & Herzegovina", "Argentina"]], ["Elliot", ["Algeria", "France"]], ["Euan", ["Australia", "Colombia"]], ["George", ["Netherlands", "Ecuador"]], ["Hannah", ["Jordan", "Germany"]], ["Jack", ["Curaçao", "Saudi Arabia"]], ["Jan", ["Belgium", "Spain"]], ["Joseph", ["Tunisia", "Sweden"]], ["Josh", ["Uruguay", "Iraq"]], ["Jonathan", ["Ivory Coast", "Switzerland"]], ["Jenny", ["Croatia", "Egypt"]], ["Kate", ["USA", "Qatar"]], ["Katie", ["Paraguay", "Morocco"]], ["Laura", ["Uzbekistan", "Czech Republic"]], ["Lou", ["Mexico", "Brazil"]], ["Matt", ["Ghana", "Haiti"]], ["Mike", ["New Zealand", "Scotland"]], ["Nick", ["England", "South Korea"]], ["Patrick", ["Norway", "Senegal"]], ["Paul", ["Portugal", "Turkey"]], ["Sophie", ["Panama", "Austria"]], ["Vic", ["Canada", "DR Congo"]]]
FLAGS = {"Algeria": "🇩🇿", "Argentina": "🇦🇷", "Australia": "🇦🇺", "Austria": "🇦🇹", "Belgium": "🇧🇪", "Bosnia & Herzegovina": "🇧🇦", "Brazil": "🇧🇷", "Canada": "🇨🇦", "Cape Verde": "🇨🇻", "Colombia": "🇨🇴", "Croatia": "🇭🇷", "Curaçao": "🇨🇼", "Czech Republic": "🇨🇿", "DR Congo": "🇨🇩", "Ecuador": "🇪🇨", "Egypt": "🇪🇬", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "France": "🇫🇷", "Germany": "🇩🇪", "Ghana": "🇬🇭", "Haiti": "🇭🇹", "Iran": "🇮🇷", "Iraq": "🇮🇶", "Ivory Coast": "🇨🇮", "Japan": "🇯🇵", "Jordan": "🇯🇴", "Mexico": "🇲🇽", "Morocco": "🇲🇦", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Norway": "🇳🇴", "Panama": "🇵🇦", "Paraguay": "🇵🇾", "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Saudi Arabia": "🇸🇦", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸", "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Tunisia": "🇹🇳", "Turkey": "🇹🇷", "USA": "🇺🇸", "Uruguay": "🇺🇾", "Uzbekistan": "🇺🇿"}
T2P = {t: p for p, ts in PLAYERS for t in ts}
TEAM_OF = {p: ts for p, ts in PLAYERS}

DATA_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"

def fetch_matches():
    req = urllib.request.Request(DATA_URL, headers={"User-Agent": "wc26-sweepstake-bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    out = []
    for m in data.get("matches", []):
        a = m.get("team1"); b = m.get("team2")
        if isinstance(a, dict): a = a.get("name")
        if isinstance(b, dict): b = b.get("name")
        sc = m.get("score") or {}
        s = None
        if sc.get("ft") or sc.get("et"):
            goals = sc.get("et") or sc.get("ft")
            s = list(goals)
            if sc.get("ps"): s += list(sc["ps"])
        out.append({"a": a, "b": b, "s": s})
    return out

def tally(matches):
    tbl = {p: {"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0} for p,_ in PLAYERS}
    played = 0
    for m in matches:
        a, b, s = m["a"], m["b"], m["s"]
        if not s or a not in FLAGS or b not in FLAGS:
            continue
        played += 1
        pens = s[2:4] if len(s) >= 4 and isinstance(s[2], int) else None
        for team, gf, ga, pd in ((a, s[0], s[1], (pens[0]-pens[1]) if pens else 0),
                                 (b, s[1], s[0], (pens[1]-pens[0]) if pens else 0)):
            p = T2P.get(team)
            if not p: continue
            r = tbl[p]; r["P"]+=1; r["GF"]+=gf; r["GA"]+=ga
            if gf>ga: r["W"]+=1
            elif gf<ga: r["L"]+=1
            elif pens: r["W"] = r["W"]+1 if pd>0 else r["W"]; r["L"] = r["L"]+1 if pd<0 else r["L"]
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
        sub = "The tournament is about to begin"
        podium = ""
        board = ('<div class="empty"><div class="big">No goals yet</div>'
                 '<p>The table wakes up the moment the first whistle blows. Check back after kick-off.</p></div>')
        podium_style = ' style="display:none"'
    else:
        leader = rows[0]
        sub = f'<b>{leader["p"]}</b> leads after <b>{played}</b> match{"" if played==1 else "es"} played'
        medals = {1:"\U0001F947", 2:"\U0001F948", 3:"\U0001F949"}
        def plinth(r, place):
            return (f'<div class="plinth p{place}"><div class="medal">{medals[place]}</div>'
                    f'<div class="nm">{r["p"]}</div><div class="pts">{r["Pts"]}</div>'
                    f'<div class="ptlabel">points</div><div class="teams">{fl(r["teams"][0],r["teams"][1])}</div>'
                    f'<div class="bar"></div></div>')
        t3 = rows[:3]
        podium = plinth(t3[1],2) + plinth(t3[0],1) + plinth(t3[2],3)
        podium_style = ""
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
        matches = fetch_matches()
    except Exception as e:
        print("fetch failed, leaving existing page:", e); return 0
    rows, played = tally(matches)
    if played == 0 and os.path.exists("leaderboard.html"):
        existing = open("leaderboard.html", encoding="utf-8").read()
        if "No goals yet" not in existing:
            print("feed shows 0 matches but page already has results; keeping existing page")
            return 0
    html = build_html(rows, played, css)
    with open("leaderboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"rebuilt leaderboard.html: {played} matches, leader {rows[0]['p'] if played else 'n/a'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
