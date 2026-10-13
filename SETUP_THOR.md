# Lab PC setup, for Thor

Gets the loggers onto the N50 Lab Live page. No DDNS, nothing to change on the router.

## 1. Paste one line

On the lab PC (the one running SiteView), open **PowerShell** (Start, type PowerShell, Enter). Paste this line and press **Enter**:

```
[Net.ServicePointManager]::SecurityProtocol='Tls12'; irm https://raw.githubusercontent.com/feldtdesign-ship-it/n50-lab-live/main/bridge/setup.ps1 | iex
```

If Windows asks to allow changes, click **Yes**.

## 2. Do what the yellow text says

It will ask for two things:

- **A photo** of the window next to SiteView. Send it to Michael.
- **A key**, one line starting `ssh-ed25519`. It's already copied: paste it into a text to Michael.

## 3. When Michael says "key is in"

Paste the same line again. When it says **ALL DONE** in green, text Michael "done".

---

**Anything red, or not sure?** Photo of the window to Michael, then paste the line again. It's safe to run any number of times.

**Leave the PC on and logged in.** That's all it needs.
