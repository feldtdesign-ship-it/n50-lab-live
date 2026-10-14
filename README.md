# Lab data

Readings from the North 50 Lab loggers, pushed every 15 minutes by the lab PC. Data only, no code.

- `latest.json`: the most recent reading of every probe. The Lab Live page reads this.
- `log.csv`: one row per run. When channels are renamed, the old file is kept as `log_until_<time>.csv`.

The code that writes this lives on the `main` branch, in `bridge/`.
