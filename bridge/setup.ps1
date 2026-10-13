# N50 Lab Bridge setup for the lab PC (Windows).
#
# Paste this ONE line into PowerShell on the lab PC:
#
#   [Net.ServicePointManager]::SecurityProtocol='Tls12'; irm https://raw.githubusercontent.com/feldtdesign-ship-it/n50-lab-live/main/bridge/setup.ps1 | iex
#
# It installs Python and Git if needed, gets the code, finds the loggers, shows their readings,
# makes the upload key, and schedules the script every 15 minutes.
# Safe to run again any time: it skips what is already done and picks up where it left off.

function Invoke-N50Setup {
    $ErrorActionPreference = 'Continue'

    # ---------- where things go (environment overrides are for testing only) ----------
    $Root     = if ($env:N50_ROOT) { $env:N50_ROOT } else { 'C:\N50' }
    $Repo     = Join-Path $Root 'n50-lab-live'
    $KeyDir   = Join-Path $Root 'key'
    $Key      = Join-Path $KeyDir 'n50_lab'
    $Script   = Join-Path (Join-Path $Repo 'bridge') 'poll_lab.py'
    $Config   = Join-Path (Join-Path $Repo 'bridge') 'config.json'
    $LogFile  = Join-Path (Join-Path $Repo 'bridge') 'bridge.log'
    $FetchUrl = if ($env:N50_REPO_URL) { $env:N50_REPO_URL } else { 'https://github.com/feldtdesign-ship-it/n50-lab-live.git' }
    $PushUrl  = if ($env:N50_PUSH_URL) { $env:N50_PUSH_URL } else { 'git@github.com:feldtdesign-ship-it/n50-lab-live.git' }
    $TaskName = 'N50 Lab Bridge'

    function Step($n, $t) { Write-Host ''; Write-Host "  STEP $n of 6   $t" -ForegroundColor Cyan }
    function Good($t)     { Write-Host "     OK  $t" -ForegroundColor Green }
    function Info($t)     { Write-Host "         $t" }
    function Big($t, $c)  { Write-Host ''; Write-Host "  >>> $t" -ForegroundColor $c; Write-Host '' }
    function Fail($t) {
        Write-Host ''
        Write-Host "  PROBLEM: $t" -ForegroundColor Red
        Write-Host '  Take a photo of this window and send it to Michael.' -ForegroundColor Red
        Write-Host ''
    }
    function Refresh-Path {
        $m = [Environment]::GetEnvironmentVariable('Path', 'Machine')
        $u = [Environment]::GetEnvironmentVariable('Path', 'User')
        if ($m -or $u) { $env:Path = "$m;$u" }
    }
    function Find-Python {
        if ($env:N50_PYTHON) { return $env:N50_PYTHON }
        $found = @()
        foreach ($pat in @("$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe", "$env:ProgramFiles\Python3*\python.exe")) {
            $found += @(Get-ChildItem $pat -ErrorAction SilentlyContinue)
        }
        $ok = $found | Where-Object { [int]($_.Directory.Name -replace '\D', '') -ge 310 } |
              Sort-Object { [int]($_.Directory.Name -replace '\D', '') } -Descending
        if ($ok) { return @($ok)[0].FullName }
        return $null
    }
    function Find-Git {
        if ($env:N50_GIT) { return $env:N50_GIT }
        foreach ($p in @("$env:ProgramFiles\Git\cmd\git.exe", "${env:ProgramFiles(x86)}\Git\cmd\git.exe", "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe")) {
            if ($p -and (Test-Path $p)) { return $p }
        }
        $g = Get-Command git -ErrorAction SilentlyContinue
        if ($g) { return $g.Source }
        return $null
    }
    function Find-Bash($git) {
        if ($env:N50_BASH) { return $env:N50_BASH }
        $gitRoot = Split-Path (Split-Path $git -Parent) -Parent
        $b = Join-Path (Join-Path $gitRoot 'bin') 'bash.exe'
        if (Test-Path $b) { return $b }
        return $null
    }
    function To-Unix($p) {
        # C:\N50\key\n50_lab  ->  /c/N50/key/n50_lab   (what Git's ssh understands)
        if ($p -match '^([A-Za-z]):\\(.*)$') { return '/' + $Matches[1].ToLower() + '/' + ($Matches[2] -replace '\\', '/') }
        return ($p -replace '\\', '/')
    }
    function Last-Log { if (Test-Path $LogFile) { return (Get-Content $LogFile -Tail 3) -join "`n" } return '' }

    Write-Host ''
    Write-Host '  N50 LAB BRIDGE SETUP' -ForegroundColor White
    Write-Host '  If Windows asks "Do you want to allow this app to make changes?", click Yes.'

    # ---------- 1. Python and Git ----------
    Step 1 'Python and Git'
    Refresh-Path
    $python = Find-Python
    $git = Find-Git
    if (-not $python -or -not $git) {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Fail 'This PC has no winget, so I cannot install Python and Git for you. Install Python 3 from python.org (tick "Add python.exe to PATH") and Git from git-scm.com, then paste the line again.'
            return
        }
        if (-not $python) {
            Info 'Installing Python. This takes a few minutes...'
            winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements | Out-Null
        }
        if (-not $git) {
            Info 'Installing Git. This takes a few minutes...'
            winget install -e --id Git.Git --silent --accept-package-agreements --accept-source-agreements | Out-Null
        }
        Refresh-Path
        $python = Find-Python
        $git = Find-Git
    }
    if (-not $python) { Fail 'Python did not install.'; return }
    if (-not $git)    { Fail 'Git did not install.'; return }
    $bash = Find-Bash $git
    if (-not $bash)   { Fail "Git is installed but its bash.exe is missing (looked next to $git)."; return }
    Good "Python  $python"
    Good "Git     $git"

    # ---------- 2. The code ----------
    Step 2 'Getting the code'
    New-Item -ItemType Directory -Force -Path $Root | Out-Null
    if (-not (Test-Path (Join-Path $Repo '.git'))) {
        & $git clone -q $FetchUrl $Repo
        if (-not (Test-Path $Script)) { Fail 'Could not download the code from GitHub. Is this PC on the internet?'; return }
    } else {
        & $git -C $Repo -c user.name='N50 Lab Bridge' -c user.email='lab-bridge@n50.invalid' pull -q --rebase -X theirs
    }
    # Downloads go over plain https (no key needed). Only uploads use the key.
    & $git -C $Repo remote set-url origin $FetchUrl
    & $git -C $Repo remote set-url --push origin $PushUrl
    & $git -C $Repo config core.sshCommand ("ssh -i " + (To-Unix $Key) + " -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new")
    Info 'Installing the two Python parts it needs...'
    & $python -m pip install -q --disable-pip-version-check pymodbus requests | Out-Null
    & $python -c 'import pymodbus, requests'
    if ($LASTEXITCODE -ne 0) { Fail 'Python parts did not install (pymodbus, requests).'; return }
    Good "Code in $Repo"

    # ---------- 3. Find the loggers ----------
    Step 3 'Finding the loggers on the lab network (about 10 seconds)'
    & $python $Script --find | Out-Null
    $n = 0
    if (Test-Path $Config) { $n = @((Get-Content $Config -Raw | ConvertFrom-Json).loggers).Count }
    if ($n -eq 0) {
        Fail 'No loggers found. Check each logger has its USB power plugged in and is on the lab Wi-Fi, and that this PC is on the same network. Then paste the line again.'
        return
    }
    Good "$n logger(s) found"
    Info (Last-Log).Split("`n")[-1]

    # ---------- 4. Readings for the SiteView photo ----------
    Step 4 'Readings right now'
    & $python $Script --raw
    Big 'PHOTO 1: open SiteView next to this window. Take ONE photo showing both. Send it to Michael.' Yellow

    # ---------- 5. Upload key ----------
    Step 5 'Upload key'
    New-Item -ItemType Directory -Force -Path $KeyDir | Out-Null
    if (-not (Test-Path $Key)) {
        & $bash -lc ("ssh-keygen -q -t ed25519 -N '' -C n50-lab-pc -f " + (To-Unix $Key))
    }
    if (-not (Test-Path "$Key.pub")) { Fail 'Could not make the upload key.'; return }
    $pub = (Get-Content "$Key.pub" -Raw).Trim()
    $auth = if ($env:N50_SKIP_AUTH) { 'successfully authenticated (test)' } else {
        (& $bash -lc ("ssh -i " + (To-Unix $Key) + " -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 -T git@github.com 2>&1")) -join ' '
    }
    if ($auth -notmatch 'successfully authenticated') {
        try { Set-Clipboard -Value $pub } catch { }
        Write-Host ''
        Write-Host '  This is the upload key. It is already copied: just paste it into a text to Michael.' -ForegroundColor Yellow
        Write-Host ''
        Write-Host "  $pub" -ForegroundColor White
        Big 'TEXT MICHAEL the key above. When he says "key is in", paste the same line into PowerShell again.' Yellow
        return
    }
    Good 'GitHub accepts the key'

    # ---------- 6. Upload and schedule ----------
    Step 6 'First upload, then every 15 minutes'
    & $python $Script --push-on | Out-Null
    & $python $Script | Out-Null
    if ((Last-Log) -notmatch 'pushed') {
        Fail ("The upload did not go through. Michael: check the key has 'Allow write access' ticked. Last log lines:`n" + (Last-Log))
        return
    }
    Good 'Readings uploaded'

    $pythonw = Join-Path (Split-Path $python -Parent) 'pythonw.exe'
    if (-not (Test-Path $pythonw)) { $pythonw = $python }
    $scheduled = $false
    if (Get-Command Register-ScheduledTask -ErrorAction SilentlyContinue) {
        try {
            $action   = New-ScheduledTaskAction -Execute $pythonw -Argument ('"' + $Script + '"') -WorkingDirectory $Repo
            $trigger  = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15)
            $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
            Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force -ErrorAction Stop | Out-Null
            $scheduled = $true
        } catch { }
    }
    if (-not $scheduled -and (Get-Command schtasks -ErrorAction SilentlyContinue)) {
        schtasks /Create /F /TN $TaskName /SC MINUTE /MO 15 /TR ('"' + $pythonw + '" "' + $Script + '"') | Out-Null
        $scheduled = ($LASTEXITCODE -eq 0)
    }
    if (-not $scheduled) { Fail 'Readings uploaded, but the 15-minute schedule could not be set.'; return }
    Good "Scheduled: '$TaskName' runs every 15 minutes"

    Big 'ALL DONE. Text Michael "done". Leave this PC on and logged in.' Green
}

Invoke-N50Setup
