# Lab bridge

**Setting up the lab PC? Follow [SETUP_THOR.md](../SETUP_THOR.md).** It is the step-by-step version of this page for Windows.

One script on the always-on lab computer. It reads the five PRECISE-LOG PL-TW loggers over Modbus TCP, reads the Davis WeatherLink Live if there is one, writes `data/latest.json` and `data/log.csv`, and pushes them to this repo so the public page updates. Nothing at the lab is exposed to the internet.

## Setup, once

1. On the lab computer: `pip install pymodbus requests`
2. Copy `config.example.json` to `config.json`. Put in each logger's IP from the UniFi client list, and the WeatherLink Live IP when it exists.
3. Fill the `channels` map from Kevin's channel schedule. The `id` is what the page shows.
4. Run `python bridge/poll_lab.py --raw` to see the raw registers, then `python bridge/poll_lab.py` once by hand, and check `data/latest.json` reads sensibly against SiteView. If the numbers are off by a factor, adjust `scale_c`. The PL-TW manual gives the register scaling; 0.1 C per count is the assumption.
5. Set `"push": true`, make sure `git push` works from that computer, and schedule the script every 15 minutes.

Windows: see step 8 of SETUP_THOR.md (Task Scheduler, `pythonw`, every 15 minutes).
Linux or macOS: `*/15 * * * * /usr/bin/python3 /path/n50-lab-live/bridge/poll_lab.py`

## What the page does with it

`index.html` fetches `data/latest.json` from the same site. When it is present and fresh, the probe table and the thermal paint use the live values and the THERM curve stays as the model line. When it is missing or stale, the page says so and falls back to the simulation.

## Register note

The PL-TW serves nine input registers, 0 to 8, as live channel readings from firmware 2.06. Which register is which channel, the open-channel marker, and the scaling need one check against SiteView on site. That is the only unknown in this script.

## Log

Every run appends to `bridge/bridge.log` on the lab PC. `config.json` and the log stay local (see `.gitignore`).
