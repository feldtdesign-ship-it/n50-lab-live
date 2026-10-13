# Lab PC setup, for Thor

This gets the five PRECISE-LOG loggers onto the N50 Lab Live page:
https://feldtdesign-ship-it.github.io/n50-lab-live/

**How it works.** One small Python script runs on the always-on lab PC every 15 minutes. It reads the loggers over the lab network (Modbus TCP, port 502), writes the readings to a file, and pushes that file to this GitHub repo. The page reads the file.

**The PC only sends out.** No DDNS, no port forwarding, nothing on the router changes. Please **do not** forward port 502 to the loggers: Modbus has no password.

About an hour, most of it step 5. Questions: Michael.

---

## 1. Install two programs

- **Python 3** from https://www.python.org/downloads/windows/. On the first screen of the installer, **tick "Add python.exe to PATH"**.
- **Git for Windows** from https://git-scm.com/download/win. Defaults are fine.

Then open **PowerShell** (Start, type PowerShell). Every command below goes there.

## 2. Make the push key and send it to Michael

The key lets this PC push to this one repo and nothing else.

```powershell
ssh-keygen -t ed25519 -C "n50-lab-pc"
```

Press **Enter** three times (default location, no passphrase; the scheduled task can't type one). If it says a key already exists and asks to overwrite, answer **n** and tell Michael.

```powershell
Get-Content $HOME\.ssh\id_ed25519.pub
```

Copy that one line (starts `ssh-ed25519`) and text or email it to Michael. It's the public half, safe to send. **Never send the file without `.pub`.**

You can carry on with steps 3 to 6 while Michael adds it.

## 3. Get the code

```powershell
mkdir C:\N50
cd C:\N50
git clone https://github.com/feldtdesign-ship-it/n50-lab-live.git
cd n50-lab-live
git remote set-url origin git@github.com:feldtdesign-ship-it/n50-lab-live.git
pip install pymodbus requests
```

## 4. Fill in the settings

```powershell
copy bridge\config.example.json bridge\config.json
notepad bridge\config.json
```

- **`loggers`**: put each logger's IP address (from the UniFi client list, names start PL). Port stays 502, unit stays 1. Delete lines for any box that isn't on the network. The names (`Vitro-1` etc.) are just labels.
- **`channels`**: one line per thermocouple that is actually wired, keyed `box name.chN`. The `id` is what the page shows, e.g. `V1 ci` = Vitro lite 1, centre, interior. The example map is Michael's guess; fix it to match the real wiring.
- **`weatherlink_ip`**: the Davis WeatherLink Live address, or `""` if there's no weather station yet.
- Leave **`push`** at `false` for now.

`config.json` stays on this PC. It is never uploaded.

## 5. Check the numbers against SiteView (the important bit)

The logger manual doesn't say how its raw numbers convert to degrees. The script assumes 0.1 °C per count. Check it:

```powershell
python bridge\poll_lab.py --raw
```

At the same moment, look at SiteView. For one box, compare channel 1 in SiteView with **register 1** in the output, channel 2 with register 2, and so on. **Send Michael a photo of both screens.**

- If the "at scale" column matches SiteView: nothing to change.
- If it's 10× off, set `scale_c` to `0.01` or `1.0` in `config.json` and run it again.
- If the channels are shifted by one (SiteView ch1 = register 0), tell Michael; it's a one-line change.
- Note the number an **unplugged** channel shows. The script treats 32767 and -32768 as "no probe".

## 6. Test run

```powershell
python bridge\poll_lab.py
```

It should end with something like `13 probes, no weather`. Open `data\latest.json` in Notepad to check it looks sensible. Every run is also written to `bridge\bridge.log`.

## 7. Turn on the upload

Once Michael says the key is added:

```powershell
ssh -T git@github.com
```

Type **yes** if it asks to trust github.com. A line saying "successfully authenticated" is good, even though it then says no shell access.

Set `"push": true` in `config.json`, then:

```powershell
python bridge\poll_lab.py
```

The last line should say **`pushed`**. Within a couple of minutes the page should show live readings.

## 8. Run it every 15 minutes

Paste these four lines into PowerShell as one block:

```powershell
$py = (Get-Command pythonw).Source
$action = New-ScheduledTaskAction -Execute $py -Argument '"C:\N50\n50-lab-live\bridge\poll_lab.py"'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "N50 Lab Bridge" -Action $action -Trigger $trigger
```

`pythonw` runs it with no window popping up over SiteView. It runs while this Windows user is logged in, so if the PC restarts, someone needs to log back in.

Check after half an hour: `bridge\bridge.log` should have new lines every 15 minutes.

---

## If something goes wrong

| What you see | What it means |
|---|---|
| `no connection to 192.168...` | That logger's IP changed or it's off. Check UniFi, fix `config.json`. |
| `modbus error` | Logger answered but refused the read. Firmware must be 2.06 or newer. |
| `git push : Permission denied (publickey)` | Key not added yet, or a different key. Redo step 2 and send Michael the `.pub` line. |
| Page says the feed is stale | The PC is off, logged out, or offline. Check `bridge\bridge.log`. |

To stop it: Task Scheduler, find **N50 Lab Bridge**, Disable.
