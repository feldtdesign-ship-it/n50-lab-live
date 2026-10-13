#!/usr/bin/env python3
"""
N50 Lab bridge. Runs on the always-on lab PC, on the same network as the loggers.

Every run it:
  1. reads each PRECISE-LOG PL-TW over Modbus TCP (input registers, live channel values),
  2. reads the Davis WeatherLink Live local API if one is present,
  3. writes data/latest.json and appends to data/log.csv,
  4. optionally commits and pushes to the n50-lab-live repo so the public page updates.

Nothing at the lab is opened to the internet. The PC only sends out.

Usage:
  python bridge/poll_lab.py          normal run (what Task Scheduler calls every 15 minutes)
  python bridge/poll_lab.py --raw    print the raw register numbers from every logger and stop.
                                     Use this once to check the scale against SiteView.

Config lives in bridge/config.json. Every run also appends to bridge/bridge.log.

Requires: pip install pymodbus requests
"""
import json, csv, os, sys, subprocess, inspect
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
LOG = os.path.join(HERE, "bridge.log")

def log(*parts):
    """Print and append to bridge/bridge.log, so scheduled runs with no window still leave a trail."""
    line = datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + " ".join(str(p) for p in parts)
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")
    except OSError:
        pass

def load_config():
    path = os.path.join(HERE, "config.json")
    if not os.path.exists(path):
        log("No bridge/config.json. Copy config.example.json to config.json and fill in the logger IPs.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

CFG = load_config()

def c_to_f(c): return None if c is None else round(c * 9 / 5 + 32, 2)

def read_registers(box):
    """Return the nine raw input registers (0 to 8) from one PL-TW, or None."""
    try:
        from pymodbus.client import ModbusTcpClient
    except ImportError:
        log("pymodbus not installed: pip install pymodbus"); return None
    cl = ModbusTcpClient(box["ip"], port=box.get("port", 502), timeout=3)
    if not cl.connect():
        log(f"{box['name']}: no connection to {box['ip']}"); return None
    try:
        # pymodbus renamed the unit argument: slave= up to 3.8, device_id= from 3.9 on.
        params = inspect.signature(cl.read_input_registers).parameters
        unit_kw = "device_id" if "device_id" in params else "slave"
        rr = cl.read_input_registers(0, count=9, **{unit_kw: box.get("unit", 1)})
        if rr.isError():
            log(f"{box['name']}: modbus error {rr}"); return None
        return list(rr.registers)
    except Exception as e:
        log(f"{box['name']}: {e}"); return None
    finally:
        cl.close()

def read_logger(box):
    """Read one PL-TW. Returns {channel_number: value_F or None}.
    PL-TW exposes nine input registers, 0 to 8, as live readings (firmware 2.06+).
    Register scaling is set in config (raw * scale + offset) once confirmed against SiteView; default assumes 0.1 C per count."""
    regs = read_registers(box)
    if regs is None: return {}
    out = {}
    for ch in range(1, 9):
        raw = regs[ch] if ch < len(regs) else None
        if raw is None: continue
        if raw >= 32768: raw -= 65536          # signed
        if raw in (-32768, 32767): out[ch] = None   # open channel markers, confirm with SiteView
        else: out[ch] = c_to_f(raw * CFG.get("scale_c", 0.1) + CFG.get("offset_c", 0.0))
    return out

def read_weatherlink():
    """Davis WeatherLink Live local API on the LAN: http://<ip>/v1/current_conditions"""
    wl = CFG.get("weatherlink_ip")
    if not wl: return None
    try:
        import requests
        j = requests.get(f"http://{wl}/v1/current_conditions", timeout=5).json()
        conds = j["data"]["conditions"]
        iss = next((c for c in conds if c.get("data_structure_type") == 1), {})
        bar = next((c for c in conds if c.get("data_structure_type") == 3), {})
        inside = next((c for c in conds if c.get("data_structure_type") == 4), {})
        return {"temp_f": iss.get("temp"), "hum": iss.get("hum"), "dew_point_f": iss.get("dew_point"),
                "wind_mph": iss.get("wind_speed_avg_last_10_min"), "wind_dir": iss.get("wind_dir_scalar_avg_last_10_min"),
                "gust_mph": iss.get("wind_speed_hi_last_10_min"), "solar_wm2": iss.get("solar_rad"),
                "rain_day_in": iss.get("rainfall_daily"), "bar_inhg": bar.get("bar_sea_level"),
                "inside_temp_f": inside.get("temp_in"), "inside_hum": inside.get("hum_in")}
    except Exception as e:
        log("weatherlink:", e); return None

def raw_dump():
    """--raw: show register 0 to 8 per logger, as stored and as signed, for the SiteView check."""
    for box in CFG["loggers"]:
        regs = read_registers(box)
        if regs is None: continue
        signed = [r - 65536 if r >= 32768 else r for r in regs]
        log(f"{box['name']} ({box['ip']})")
        for i, (r, s) in enumerate(zip(regs, signed)):
            log(f"   register {i}: {r}   signed {s}   at scale {CFG.get('scale_c', 0.1)} = {s * CFG.get('scale_c', 0.1) + CFG.get('offset_c', 0.0):.2f} C")

def git(*args):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)
    if r.returncode != 0 and r.stderr.strip():
        log("git", args[0], ":", r.stderr.strip().splitlines()[-1])
    return r.returncode

def push(now):
    # Identity for the commit only, so the lab PC needs no global git setup.
    who = ["-c", "user.name=N50 Lab Bridge", "-c", "user.email=lab-bridge@n50.invalid"]
    git("add", "data")
    git(*who, "commit", "-q", "-m", f"lab data {now}")
    # Pick up any page changes made from New York before pushing, or the push is refused.
    git(*who, "pull", "-q", "--rebase", "-X", "theirs")
    if git("push", "-q") == 0: log("pushed")

def main():
    if "--raw" in sys.argv:
        raw_dump(); return
    os.makedirs(DATA, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    probes = {}
    for box in CFG["loggers"]:
        vals = read_logger(box)
        for ch, v in vals.items():
            key = f"{box['name']}.ch{ch}"
            meta = CFG.get("channels", {}).get(key, {})
            probes[meta.get("id", key)] = {"value_f": v, "box": box["name"], "ch": ch, **meta}
    wx = read_weatherlink()
    latest = {"time_utc": now, "site": CFG.get("site", "North 50 Lab"), "probes": probes, "weather": wx}
    with open(os.path.join(DATA, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, indent=1)
    # rolling CSV, one row per run, one column per probe
    cols = ["time_utc"] + sorted(probes) + (["wx_temp_f", "wx_hum", "wx_wind_mph"] if wx else [])
    path = os.path.join(DATA, "log.csv"); new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new: w.writerow(cols)
        row = [now] + [probes[k]["value_f"] for k in sorted(probes)] + ([wx["temp_f"], wx["hum"], wx["wind_mph"]] if wx else [])
        w.writerow(row)
    log(now, len(probes), "probes,", "weather ok" if wx else "no weather")
    if CFG.get("push"):
        push(now)

if __name__ == "__main__":
    main()
