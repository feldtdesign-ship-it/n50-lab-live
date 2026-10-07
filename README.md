# North 50 Lab Live

A simulated sensor dashboard for the North 50 Building Systems window lab in Fairbanks, Alaska, with real weather behind it.

**Live page:** https://feldtdesign-ship-it.github.io/n50-lab-live/

## What is real and what is not

- **Weather is real.** Open-Meteo at the lab's own coordinates and elevation, 1,204 ft, refreshed every 10 minutes and seven days back, plus the same model at Fairbanks International and the live airport observation from the National Weather Service for the valley reference.
- **Probe readings are simulated.** Each station takes the fraction of the room-to-outdoor temperature difference that the N50 THERM model dropped at that point, and applies it to the outdoor temperature right now. When the lab's loggers stream, these panels take the real numbers and the model line stays as the thing to beat.
- **The window walls are a Blender model.** The Vitro Wall is three 44 by 86 inch vacuum insulated glass units under three transoms. The LuxWall openings are assumed at 36 by 80 inches. Every lite carries three Type T thermocouples, centre inside, centre outside, edge inside, and each wall has two interior and two exterior air thermocouples. The loggers are Microedge PRECISE-LOG PL-TW, sampling every 15 minutes.
- **The inversion tracker** compares the lab on the slope against the valley floor. Fourteen real stations, October through March, say the slope runs 10 to 20 F warmer than Fairbanks International on inversion nights. The models apply a lapse rate and show the opposite, which is why the lab needs its own weather station.

## Going live

`bridge/` holds the script that runs on the lab computer, reads the loggers over Modbus and the Davis WeatherLink Live on the LAN, and pushes `data/latest.json` here every 15 minutes. The page reads that file and switches from simulation to live on its own. See `bridge/README.md`.

## Files

- `index.html` is the whole page, self-contained. Open it locally or serve it anywhere.
- `model/n50_window_banks.glb` is the Blender export of the two walls with probes.
- `build/build_banks_blender.py` builds the walls in Blender 5.
- `build/gen_dash.py` generates the page from the model and embedded assets.

## Credits

North 50 Building Systems. Dashboard, model, and thermal simulation by Feldt Design. Weather by Open-Meteo and the National Weather Service.
