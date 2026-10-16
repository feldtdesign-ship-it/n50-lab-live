#!/usr/bin/env python3
"""
N50 lab: read both test walls from SiteView-Web and post them to the lab page.

Small on purpose. Nothing is installed at the lab. It listens to SiteView-Web's own
live feed (the same one the dashboard uses), picks out every channel Kevin has named,
and writes latest.json to the lab-data branch that the page reads.

  python3 siteview_lab.py            test: listen, print the readings, upload nothing
  python3 siteview_lab.py --upload   same, then post latest.json to the page

The SiteView address comes from N50_SV_URL (a GitHub secret when run on GitHub).

Login: as of 2026-10-16 the live feed answers without one. If Kevin locks it, set N50_SV_USER
(and N50_SV_PASS, or type it when asked). The password is never written to disk.
Upload uses the GitHub CLI login on this Mac (gh), or GITHUB_TOKEN when run on GitHub.
"""
import os, sys, json, re, time, base64, getpass, subprocess
from datetime import datetime, timezone
import requests

BASE = os.environ.get("N50_SV_URL", "").rstrip("/")
if not BASE: sys.exit("Set N50_SV_URL to the SiteView-Web address.")
REPO = "feldtdesign-ship-it/n50-lab-live"
BRANCH = "lab-data"
RS = "\x1e"            # SignalR message separator
LISTEN_S = 150         # SiteView pushes about once a minute

# Logger serial -> channel -> page probe, from Kevin's SiteView channel names of 2026-10-16.
# Channel 0 on every logger is its built-in sensor and is skipped. Air probes carry the wall
# letter (A Vitro, B LuxWall) so they land on the right wall. Box 5 channels 1 to 4 are still
# unnamed in SiteView and are left out until Kevin names them.
WALLS = {
    "060300603213": {1: "V1 ce", 2: "V2 ce", 3: "A:air out 1", 4: "A:air in 1", 5: "V1 ci", 6: "V1 ei"},
    "060300603312": {1: "V3 ce", 2: "V2 ci", 3: "V2 ei", 4: "V3 ci", 5: "V3 ei"},
    "060300603214": {1: "L5 ci", 2: "L5 ei", 3: "L4 ci", 4: "L4 ei", 5: "L1 ci", 6: "L1 ei", 7: "L2 ci", 8: "B:air in 1"},
    "060300603316": {1: "L3 ci", 2: "L3 ei", 3: "L6 ci", 4: "L6 ei", 5: "L2 ei"},
    "060300603315": {5: "L5 ce", 6: "L6 ce", 7: "B:air out 1"},
}
NAMES = {"060300603213": "#1", "060300603312": "#2", "060300603214": "#3", "060300603316": "#4", "060300603315": "5"}

def login(s):
    """Sign in only if SiteView sends us to the sign-in page."""
    user = os.environ.get("N50_SV_USER")
    if not user: return
    page = s.get(BASE + "/", timeout=20).text
    tok = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', page)
    pw = os.environ.get("N50_SV_PASS") or getpass.getpass("SiteView password for %s: " % user)
    r = s.post(BASE + "/", data={"Username": user, "Password": pw, "ReturnURL": "home",
               "__RequestVerificationToken": tok.group(1) if tok else ""}, timeout=20)
    if "Please sign in" in r.text: sys.exit("SiteView did not accept the login.")
    print("signed in as", user)

def to_f(text):
    """'35.43 °F' -> 35.43. Returns None for blanks, errors and broken-probe values."""
    m = re.search(r"-?\d+(?:\.\d+)?", text or "")
    if not m: return None
    v = float(m.group())
    if "C" in text and "F" not in text: v = v * 9 / 5 + 32
    return round(v, 2) if -80 < v < 200 else None

def listen():
    s = requests.Session()
    login(s)
    neg = s.post(BASE + "/localsignalrhub/negotiate?negotiateVersion=1",
                 headers={"Content-Length": "0"}, timeout=20)
    neg.raise_for_status()
    url = BASE + "/localsignalrhub?id=" + neg.json()["connectionToken"]
    send = lambda o: s.post(url, data=json.dumps(o) + RS, timeout=20)
    send({"protocol": "json", "version": 1})
    got, joined, end = {}, False, time.time() + LISTEN_S
    while time.time() < end and len(got) < len(WALLS):
        r = s.get(url, timeout=120)
        if r.status_code != 200: sys.exit("SiteView feed closed (%s)" % r.status_code)
        for raw in filter(None, r.text.split(RS)):
            m = json.loads(raw)
            if m.get("type") == 1 and m.get("target") == "DeviceRealtimeUpdated":
                d = json.loads(m["arguments"][0])
                if d.get("serialNumber") in WALLS: got[d["serialNumber"]] = d
        if not joined:
            send({"type": 1, "target": "FrontendRequestJoin", "arguments": []})
            send({"type": 1, "target": "RequestOnlineDevices", "arguments": []})
            joined = True
    return got

def build(got):
    probes = {}
    for sn, chans in WALLS.items():
        d = got.get(sn)
        if not d: continue
        for c in d.get("channels", []):
            pid = chans.get(c.get("chIndex"))
            if not pid: continue
            ok = d.get("isOnline", True) and c.get("validEquation", True)
            raw = c.get("value")
            v = round(raw, 2) if ok and isinstance(raw, (int, float)) and -80 < raw < 200 else (to_f(c.get("valueString")) if ok else None)
            probes[pid] = {"value_f": v, "box": NAMES[sn], "ch": c.get("chIndex"),
                           "label": c.get("valueString"), "time": c.get("time")}
    return {"time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "site": "North 50 Lab", "source": "SiteView-Web",
            "probes": probes, "weather": None}

def github_token():
    if os.environ.get("GITHUB_TOKEN"): return os.environ["GITHUB_TOKEN"]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()

def upload(doc):
    h = {"Authorization": "Bearer " + github_token(), "Accept": "application/vnd.github+json"}
    api = "https://api.github.com/repos/%s/contents/latest.json" % REPO
    cur = requests.get(api, params={"ref": BRANCH}, headers=h, timeout=20)
    body = {"message": "lab data " + doc["time_utc"], "branch": BRANCH,
            "content": base64.b64encode(json.dumps(doc, indent=1).encode()).decode()}
    if cur.status_code == 200: body["sha"] = cur.json()["sha"]
    r = requests.put(api, json=body, headers=h, timeout=30)
    r.raise_for_status()
    print("uploaded to", BRANCH)

def main():
    got = listen()
    doc = build(got)
    print("\nReadings, compare with SiteView Real-Time:")
    for pid, p in sorted(doc["probes"].items()):
        print("  %-12s box %s ch%s   %s" % (pid, p["box"], p["ch"], p["label"]))
    missing = [NAMES[sn] for sn in WALLS if sn not in got]
    if missing: print("No reading yet from logger", ", ".join(missing))
    bad = sorted(k for k, p in doc["probes"].items() if p["value_f"] is None)
    if bad: print("Left blank, reading out of range:", ", ".join(bad))
    if not doc["probes"]: sys.exit("Nothing received. Nothing uploaded.")
    if "--upload" in sys.argv: upload(doc)
    else: print("\nTest only. Nothing uploaded.")

if __name__ == "__main__":
    main()
