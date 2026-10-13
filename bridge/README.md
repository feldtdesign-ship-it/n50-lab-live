# Lab bridge

**Setting up the lab PC? Follow [SETUP_THOR.md](../SETUP_THOR.md).** One pasted line runs `setup.ps1`, which does everything below.

`poll_lab.py` runs on the always-on lab PC every 15 minutes. It reads the PRECISE-LOG PL-TW loggers over Modbus TCP and the Davis WeatherLink Live if set, writes `data/latest.json` and `data/log.csv`, and pushes them to this repo so the page updates. Nothing at the lab is exposed to the internet: the PC only sends out, so no DDNS and no port forwarding.

## What setup.ps1 does

1. Installs Python 3.12 and Git with winget if missing.
2. Clones this repo to `C:\N50\n50-lab-live`. Fetch is over https (no key); push is over ssh with a key kept in `C:\N50\key`.
3. `poll_lab.py --find` scans the PC's /24 for port 502 and keeps whatever answers like a PL-TW. Loggers are named `PL-` plus the last number of their IP.
4. `poll_lab.py --raw` prints readings for the SiteView photo.
5. Makes the key, copies the public half to the clipboard, and stops until GitHub accepts it. Michael adds it as a deploy key with write access.
6. `--push-on`, first push, then a scheduled task **N50 Lab Bridge** every 15 minutes with `pythonw` (no window).

Rerunning it is safe; it skips what's done.

## Settings

- `bridge/lab.json`, in the repo, edited from New York: `scale_c`, `offset_c`, `weatherlink_ip`, `boxes`, and `channels`. The lab PC pulls it every run.
- `boxes` maps each logger's hardware (MAC) address to its name, e.g. `"aa:bb:cc:dd:ee:ff": "VW-1"`. `--find` records the address from the PC's ARP table. If a logger stops answering, each run looks for its hardware address elsewhere on the network and updates its IP, so names survive the router handing out new addresses. No router changes needed.
- `bridge/config.json`, on the lab PC only, written by `--find`: logger addresses and `push`.

Channel keys are `<box name>.chN`, e.g. `"VW-1.ch1": {"id": "V1 ci", "wall": "A", "lite": "V1", "face": "in", "station": "centre"}`. The `id` is what the page shows. Renaming channels starts a new `log.csv`; the old one is kept as `log_until_<time>.csv`.

## Register note

The PL-TW serves nine input registers, 0 to 8, as live readings from firmware 2.06. Registers 1 to 8 are assumed to be channels 1 to 8 at 0.1 C per count, with 32767 and -32768 as open channel. The SiteView photo confirms or corrects this; fix it in `lab.json`.

## Log

Every run appends to `bridge/bridge.log` on the lab PC.
