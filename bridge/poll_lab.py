#!/usr/bin/env python3
"""
N50 Lab bridge. Runs on the always-on lab PC, on the same network as the loggers.

Every run it:
  1. pulls this repo, so channel names and scale set from New York (bridge/lab.json) take effect,
  2. reads each PRECISE-LOG PL-TW over Modbus TCP (input registers, live channel values),
  3. reads the Davis WeatherLink Live local API if one is set,
  4. writes data/latest.json and appends to data/log.csv,
  5. commits and pushes data/ so the public page updates.

Nothing at the lab is opened to the internet. The PC only sends out.

Usage:
  python bridge/poll_lab.py          normal run (what Task Scheduler calls every 15 minutes)
  python bridge/poll_lab.py --find   scan the lab network for loggers and write bridge/config.json
  python bridge/poll_lab.py --raw    print every logger's readings for the SiteView check, and stop
  python bridge/poll_lab.py --push-on  switch on uploading in config.json

Settings:
  bridge/lab.json     shared, in the repo: scale, channel names, weather station. Edited from New York.
  bridge/config.json  this PC only, written by --find: logger addresses and whether to push.
Every run also appends to bridge/bridge.log.

Requires: pip install pymodbus requests
Normal setup on Windows is bridge/setup.ps1, which does all of this.
"""
import json, csv, os, re, sys, socket, subprocess, inspect, shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
LOG = os.path.join(HERE, "bridge.log")
LOCAL = os.path.join(HERE, "config.json")
CFG = {}

def log(*parts):
    """Print and append to bridge/bridge.log, so scheduled runs with no window still leave a trail."""
    line = datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + " ".join(str(p) for p in parts)
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")
    except OSError:
        pass

def read_json(path):
    if not os.path.exists(path): return {}
    with open(path, encoding="utf-8") as f: return json.load(f)

def load_config():
    """Shared lab.json first, then this PC's config.json on top."""
    CFG.clear()
    CFG.update(read_json(os.path.join(HERE, "lab.json")))
    CFG.update(read_json(LOCAL))
    CFG.setdefault("loggers", [])
    # Names set from New York in lab.json "boxes", keyed by hardware address, win over PL-<n>.
    for box in CFG["loggers"]:
        box["name"] = CFG.get("boxes", {}).get(box.get("mac") or "", box["name"])

def parse_arp(text):
    """{ip: mac} from `arp -a` output, Windows (aa-bb-..) or macOS/Linux (a:b:..) style."""
    table = {}
    for line in text.splitlines():
        ip = re.search(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b", line)
        mac = re.search(r"(?<![0-9A-Fa-f:-])([0-9A-Fa-f]{1,2}(?:[:-][0-9A-Fa-f]{1,2}){5})(?![0-9A-Fa-f:-])", line)
        if ip and mac:
            m = ":".join(part.zfill(2) for part in re.split("[:-]", mac.group(1))).lower()
            if m not in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"): table[ip.group(1)] = m
    return table

def arp_table():
    """The PC's own list of hardware addresses for devices it has just talked to. Read-only."""
    try:
        return parse_arp(subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=15).stdout)
    except Exception:
        return {}

def c_to_f(c): return None if c is None else round(c * 9 / 5 + 32, 2)

def read_registers(box, quiet=False):
    """Return the nine raw input registers (0 to 8) from one PL-TW, or None."""
    from pymodbus.client import ModbusTcpClient
    cl = ModbusTcpClient(box["ip"], port=box.get("port", 502), timeout=3)
    if not cl.connect():
        if not quiet: log(f"{box['name']}: no connection to {box['ip']}")
        return None
    try:
        # pymodbus renamed the unit argument: slave= up to 3.8, device_id= from 3.9 on.
        params = inspect.signature(cl.read_input_registers).parameters
        unit_kw = "device_id" if "device_id" in params else "slave"
        rr = cl.read_input_registers(0, count=9, **{unit_kw: box.get("unit", 1)})
        if rr.isError():
            if not quiet: log(f"{box['name']}: modbus error {rr}")
            return None
        return list(rr.registers)
    except Exception as e:
        if not quiet: log(f"{box['name']}: {e}")
        return None
    finally:
        cl.close()

def to_c(raw):
    """Raw register to degrees C, or None for an open channel."""
    if raw >= 32768: raw -= 65536          # signed
    if raw in (-32768, 32767): return None  # open channel markers, confirm with SiteView
    return raw * CFG.get("scale_c", 0.1) + CFG.get("offset_c", 0.0)

def read_logger(box):
    """Read one PL-TW. Returns {channel_number: value_F or None}.
    PL-TW exposes nine input registers, 0 to 8, as live readings (firmware 2.06+).
    Scale is set in lab.json once confirmed against SiteView; default assumes 0.1 C per count."""
    regs = read_registers(box)
    if regs is None: return {}
    return {ch: c_to_f(to_c(regs[ch])) for ch in range(1, 9) if ch < len(regs)}

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

# ---------- setup helpers ----------

def lan_prefix():
    """First three numbers of this PC's address on the lab network, e.g. 192.168.1"""
    if os.environ.get("N50_SUBNET"): return os.environ["N50_SUBNET"]   # for testing
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]   # no packet is sent
    finally:
        s.close()
    return ip.rsplit(".", 1)[0]

MODBUS_PORT = int(os.environ.get("N50_PORT", 502))   # override for testing only

def port_open(ip, port=MODBUS_PORT):
    try:
        with socket.create_connection((ip, port), timeout=0.6): return ip
    except OSError:
        return None

def scan():
    """Addresses on the PC's /24 answering on the Modbus port."""
    pre = lan_prefix()
    with ThreadPoolExecutor(64) as ex:
        return [ip for ip in ex.map(port_open, [f"{pre}.{i}" for i in range(1, 255)]) if ip]

def find_loggers():
    """--find: scan the /24 for Modbus on 502, keep the ones that answer like a PL-TW, note each one's
    hardware address, write config.json."""
    log(f"Looking for loggers on {lan_prefix()}.1 to {lan_prefix()}.254 ...")
    hits = scan()
    found = []
    for ip in sorted(hits, key=lambda a: int(a.rsplit(".", 1)[1])):
        box = {"name": f"PL-{ip.rsplit('.', 1)[1]}", "ip": ip, "port": MODBUS_PORT, "unit": 1}
        if read_registers(box, quiet=True) is not None: found.append(box)
    arp = arp_table()
    for box in found:
        box["mac"] = arp.get(box["ip"], "")
    local = read_json(LOCAL)
    local["loggers"] = found
    local.setdefault("push", False)
    with open(LOCAL, "w", encoding="utf-8") as f: json.dump(local, f, indent=1)
    log(f"Found {len(found)} logger(s): " + (", ".join(f"{b['name']} at {b['ip']}" for b in found) or "none"))
    return len(found)

def relocate():
    """If a logger stopped answering at its address, look for its hardware address elsewhere on the
    network (the router may have given it a new one) and update config.json. No router changes needed."""
    missing = [b for b in CFG["loggers"] if b.get("mac") and not port_open(b["ip"], b.get("port", MODBUS_PORT))]
    if not missing: return
    log("Not answering:", ", ".join(b["name"] for b in missing), "- looking for them by hardware address")
    scan()
    where = {mac: ip for ip, mac in arp_table().items()}
    lost = {b["mac"] for b in missing}
    local = read_json(LOCAL); moved = 0
    for saved in local.get("loggers", []):
        new_ip = where.get(saved.get("mac"))
        if saved.get("mac") in lost and new_ip and new_ip != saved["ip"]:
            log(f"{saved['mac']} moved {saved['ip']} -> {new_ip}"); saved["ip"] = new_ip; moved += 1
    if moved:
        with open(LOCAL, "w", encoding="utf-8") as f: json.dump(local, f, indent=1)
        load_config()

def raw_dump():
    """--raw: one table per logger, for a photo next to SiteView."""
    print()
    print("  Compare with SiteView. Take ONE photo showing this window AND SiteView. Send it to Michael.")
    print()
    for box in CFG["loggers"]:
        regs = read_registers(box)
        if regs is None: continue
        print(f"  {box['name']}   ({box['ip']}, hardware {box.get('mac') or 'unknown'})")
        for ch in range(1, 9):
            if ch >= len(regs): break
            c = to_c(regs[ch])
            shown = "  no probe" if c is None else f"{c:8.1f} C"
            print(f"     channel {ch}: {shown}      raw {regs[ch]}")
        print(f"     (register 0: raw {regs[0]})")
        print()
    log("raw readings shown for", len(CFG["loggers"]), "logger(s)")

def git_exe():
    """git on PATH, or Git for Windows' usual place if a scheduled run hasn't picked up PATH yet."""
    for p in (shutil.which("git"), r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files (x86)\Git\cmd\git.exe"):
        if p and os.path.exists(p): return p
    return "git"

def git(*args):
    r = subprocess.run([git_exe(), "-C", ROOT, *args], capture_output=True, text=True)
    if r.returncode != 0 and r.stderr.strip():
        log("git", args[0], ":", r.stderr.strip().splitlines()[-1])
    return r.returncode

WHO = ["-c", "user.name=N50 Lab Bridge", "-c", "user.email=lab-bridge@n50.invalid"]

def push(now):
    git("add", "data")
    git(*WHO, "commit", "-q", "-m", f"lab data {now}")
    # Pick up any page changes made from New York before pushing, or the push is refused.
    git(*WHO, "pull", "-q", "--rebase", "-X", "theirs")
    if git("push", "-q") == 0: log("pushed")

def main():
    if "--find" in sys.argv:
        load_config(); find_loggers(); return
    if "--push-on" in sys.argv:
        local = read_json(LOCAL); local["push"] = True
        with open(LOCAL, "w", encoding="utf-8") as f: json.dump(local, f, indent=1)
        log("upload switched on"); return
    load_config()
    if CFG.get("push"):
        git(*WHO, "pull", "-q", "--rebase", "-X", "theirs")   # fresh lab.json from New York
        load_config()
    if not CFG["loggers"]:
        log("No loggers in bridge/config.json. Run setup again (or: python bridge/poll_lab.py --find).")
        sys.exit(1)
    relocate()
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
    if not new:
        with open(path, encoding="utf-8") as f: old_cols = f.readline().strip().split(",")
        if old_cols != cols:   # channels renamed or a logger added: keep the old file, start a new one
            os.replace(path, os.path.join(DATA, f"log_until_{now[:19].replace(':', '')}.csv")); new = True
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
