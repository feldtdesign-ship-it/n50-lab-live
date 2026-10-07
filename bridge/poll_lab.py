#!/usr/bin/env python3
"""
N50 Lab bridge. Runs on the always-on lab computer, on the same network as the loggers.

Every run it:
  1. reads each PRECISE-LOG PL-TW over Modbus TCP (input registers, live channel values),
  2. reads the Davis WeatherLink Live local API if one is present,
  3. writes data/latest.json and appends to data/log.csv,
  4. optionally commits and pushes to the n50-lab-live repo so the public page updates.

Schedule it every 15 minutes (Task Scheduler on Windows, cron on Linux or macOS) to match the logger sample rate.

Config lives in bridge/config.json. Fill in the logger IPs and the channel map from Kevin's schedule.

Requires: pip install pymodbus requests
"""
import json, csv, os, sys, time, subprocess
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CFG = json.load(open(os.path.join(HERE, "config.json")))
DATA = os.path.join(ROOT, "data"); os.makedirs(DATA, exist_ok=True)

def c_to_f(c): return None if c is None else round(c * 9 / 5 + 32, 2)

def read_logger(box):
    """Read one PL-TW. Returns {channel_number: value_F or None}.
    PL-TW exposes nine input registers, 0 to 8, as live readings (firmware 2.06+).
    Register scaling is set in config (raw * scale + offset) once confirmed against SiteView; default assumes 0.1 C per count."""
    try:
        from pymodbus.client import ModbusTcpClient
    except ImportError:
        print("pymodbus not installed: pip install pymodbus"); return {}
    cl = ModbusTcpClient(box["ip"], port=box.get("port", 502), timeout=3)
    out = {}
    if not cl.connect():
        print(f"{box['name']}: no connection to {box['ip']}"); return {}
    try:
        rr = cl.read_input_registers(0, count=9, slave=box.get("unit", 1))
        if rr.isError():
            print(f"{box['name']}: modbus error {rr}"); return {}
        regs = rr.registers
        for ch in range(1, 9):
            raw = regs[ch] if ch < len(regs) else None
            if raw is None: continue
            if raw >= 32768: raw -= 65536          # signed
            if raw in (-32768, 32767): out[ch] = None   # open channel markers, confirm with SiteView
            else: out[ch] = c_to_f(raw * CFG.get("scale_c", 0.1) + CFG.get("offset_c", 0.0))
    finally:
        cl.close()
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
        print("weatherlink:", e); return None

def main():
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
    json.dump(latest, open(os.path.join(DATA, "latest.json"), "w"), indent=1)
    # rolling CSV, one row per run, one column per probe
    cols = ["time_utc"] + sorted(probes) + (["wx_temp_f", "wx_hum", "wx_wind_mph"] if wx else [])
    path = os.path.join(DATA, "log.csv"); new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(cols)
        row = [now] + [probes[k]["value_f"] for k in sorted(probes)] + ([wx["temp_f"], wx["hum"], wx["wind_mph"]] if wx else [])
        w.writerow(row)
    print(now, len(probes), "probes", "weather ok" if wx else "no weather")
    if CFG.get("push"):
        subprocess.run(["git", "-C", ROOT, "add", "data"], check=False)
        subprocess.run(["git", "-C", ROOT, "commit", "-q", "-m", f"lab data {now}"], check=False)
        subprocess.run(["git", "-C", ROOT, "push", "-q"], check=False)

if __name__ == "__main__":
    main()
