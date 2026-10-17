# Lab bridge

**Current route, 2026-10-16:** `siteview_lab.py` runs on GitHub every 15 minutes (`.github/workflows/lab-data.yml`). It reads SiteView-Web's live feed and posts `latest.json` to the `lab-data` branch. Nothing is installed at the lab. The SiteView address is the repo secret `N50_SV_URL`. Channel names come from Kevin's SiteView list, mapped in the script. The `poll_lab.py` and `setup.ps1` route below was never run and is on hold.

**Setting up the lab PC? Follow [SETUP_THOR.md](../SETUP_THOR.md).** One pasted line runs `setup.ps1`, which does everything below.

`poll_lab.py` runs on the always-on lab PC every 15 minutes. It reads the thermocouple loggers over Modbus TCP and a weather station if set, writes `latest.json` and `log.csv`, and pushes them to the **`lab-data` branch**, which holds data only. The page reads `latest.json` from that branch. Nothing at the lab is exposed to the internet: the PC only sends out, so no DDNS and no port forwarding.

## Safety on a PC we don't own

- **Read only.** The only Modbus request is read input registers. Nothing is ever written to a logger.
- **Nothing listens.** No server, no open port, no router or firewall change. Outbound only: HTTPS to GitHub and SSH to github.com for the upload.
- **No code arrives on its own.** The scheduled run never pulls code. It downloads `bridge/lab.json` as plain data, keeps only known keys of the right type (`site`, `scale_c`, `offset_c`, `weatherlink_ip`, `boxes`, `channels`), and caches it in `bridge/lab_cache.json`. The code on the PC changes only when someone re-runs setup on purpose.
- **Runs as a normal user.** The scheduled task is not elevated. Git's installer asks for Windows permission once.
- **Shared loggers.** SiteView talks to the same loggers. The script connects for a few seconds every 15 minutes. Watch SiteView on the first run in case the PL-TW limits simultaneous connections.
- **The search.** `--find` (setup, and when a logger goes missing) tries port 502 on every address in the /24. UniFi threat detection may flag it as a scan.

## What setup.ps1 does

1. Installs Python 3.12 and Git with winget if missing.
2. Clones this repo to `C:\N50\n50-lab-live`. Fetch is over https (no key); push is over ssh with a key kept in `C:\N50\key`. The first upload clones the `lab-data` branch to `C:\N50\lab-data` and pushes only there.
3. `poll_lab.py --find` scans the PC's /24 for port 502 and keeps whatever answers like a PL-TW. Loggers are named `PL-` plus the last number of their IP.
4. `poll_lab.py --raw` prints readings for the SiteView photo.
5. Makes the key, copies the public half to the clipboard, and stops until GitHub accepts it. Michael adds it as a deploy key with write access.
6. `--push-on`, first push, then a scheduled task **N50 Lab Bridge** every 15 minutes with `pythonw` (no window).

Rerunning it is safe; it skips what's done.

## Settings

- `bridge/lab.json`, in the repo, edited from New York: `scale_c`, `offset_c`, `weatherlink_ip`, `boxes`, and `channels`. The lab PC downloads it as data every run (changes show within about 5 minutes of the GitHub cache).
- `boxes` maps each logger's hardware (MAC) address to its name, e.g. `"aa:bb:cc:dd:ee:ff": "VW-1"`. `--find` records the address from the PC's ARP table. If a logger stops answering, each run looks for its hardware address elsewhere on the network and updates its IP, so names survive the router handing out new addresses. No router changes needed.
- `bridge/config.json`, on the lab PC only, written by `--find`: logger addresses and `push`.

Channel keys are `<box name>.chN`, e.g. `"VW-1.ch1": {"id": "V1 ci", "wall": "A", "lite": "V1", "face": "in", "station": "centre"}`. The `id` is what the page shows. Renaming channels starts a new `log.csv` on the `lab-data` branch; the old one is kept as `log_until_<time>.csv`.

## Register note

The PL-TW serves nine input registers, 0 to 8, as live readings from firmware 2.06. Registers 1 to 8 are assumed to be channels 1 to 8 at 0.1 C per count, with 32767 and -32768 as open channel. The SiteView photo confirms or corrects this; fix it in `lab.json`.

## Log

Every run appends to `bridge/bridge.log` on the lab PC.
