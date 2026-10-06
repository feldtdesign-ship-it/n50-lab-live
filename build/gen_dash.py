#!/usr/bin/env python3
"""Generate the North 50 Lab Live dashboard HTML with embedded assets."""
import base64, os
S = os.path.dirname(os.path.abspath(__file__))
def b64(p, mime): return f"data:{mime};base64," + base64.b64encode(open(p,"rb").read()).decode()
MARK = b64(f"{S}/mark_cream.png", "image/png")
CAM_H = ""
CAM_L = ""
GLB = b64(f"{S}/n50_banks.glb", "model/gltf-binary")
IR1 = ""; IR2 = ""

HTML = r"""<title>North 50 Lab Live</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a lab wall. Dark field, navy panels, amber for the live thing, ice for cold, ember for warm. Single dark theme by choice. */
:root{
  --night:#06101B; --panel:#0E2238; --panel2:#153050; --navy:#315377; --line:#27446A;
  --cream:#F5F2EA; --mute:#9DB0C6; --dim:#5E7490;
  --amber:#EBB540; --ice:#9FD9E8; --ember:#F4B860; --warm:#E8743B; --cold:#4FA3C7; --ok:#3DDCA8;
  --display:"Archivo",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--night);color:var(--cream);font-family:var(--display);font-size:14px;line-height:1.45;padding-block:0 32px;padding-inline:20px}
a{color:var(--amber)}
.wrap{max-width:1240px;margin:0 auto}
header{display:flex;align-items:center;gap:18px;flex-wrap:wrap;padding:18px 0 14px;border-bottom:1px solid var(--line)}
header img{height:26px;width:auto}
.hd-title{font-weight:600;letter-spacing:.14em;font-size:12px;text-transform:uppercase;color:var(--mute)}
.hd-title b{color:var(--cream);font-weight:600}
.clock{font-family:var(--mono);font-size:13px;color:var(--cream);margin-left:auto;font-variant-numeric:tabular-nums}
.pill{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;padding:4px 9px;border:1px solid var(--line);border-radius:3px;color:var(--mute);white-space:nowrap}
.pill.live{border-color:var(--ok);color:var(--ok)}
.pill.live::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--ok);margin-right:7px;vertical-align:1px;animation:blink 2s infinite}
.pill.sim{border-color:var(--amber);color:var(--amber)}
@keyframes blink{50%{opacity:.25}}
@media (prefers-reduced-motion:reduce){.pill.live::before{animation:none}}
.grid{display:grid;gap:14px;margin-top:14px}
.g5{grid-template-columns:repeat(5,minmax(0,1fr))}
.g2{grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)}
.g2b{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
@media (max-width:900px){.g5{grid-template-columns:repeat(2,minmax(0,1fr))}.g2,.g2b{grid-template-columns:1fr}}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:14px 16px;min-width:0}
.panel h2{margin:0 0 10px;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);font-weight:600;display:flex;align-items:center;gap:10px}
.panel h2 .tag{margin-left:auto;font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--dim);text-transform:none}
.tile .v{font-family:var(--mono);font-size:26px;line-height:1;font-variant-numeric:tabular-nums;color:var(--cream);margin:2px 0 4px}
.tile .v small{font-size:13px;color:var(--mute);margin-left:3px}
.tile .s{font-size:11.5px;color:var(--mute)}
.spark{display:block;width:100%;height:34px;margin-top:8px}
.ctlbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:14px;padding:10px 16px}
.ctlbar label{font-family:var(--mono);font-size:10.5px;color:var(--dim);letter-spacing:.06em}
.ctlbar .sep{width:1px;height:18px;background:var(--line);margin:0 6px}
.ctlbar .kick{font-family:var(--mono);font-size:10px;letter-spacing:.14em;color:var(--amber);margin-right:6px}
.stagewrap{position:relative}
.ov{position:absolute;left:10px;top:10px;font-family:var(--mono);font-size:10px;line-height:1.55;color:var(--cream);background:rgba(6,16,27,.72);padding:7px 10px;border-radius:2px;border-left:2px solid var(--amber);pointer-events:none}
.tscale{position:absolute;right:10px;top:10px;bottom:10px;width:46px;display:flex;flex-direction:column;align-items:center;font-family:var(--mono);font-size:10px;color:var(--cream);pointer-events:none}
.tscale i{flex:1;width:10px;margin:4px 0;border-radius:2px;background:linear-gradient(180deg,#ffffff,#ffe56b,#ff9a1f,#e8321c,#8a0a6e,#1a0238,#000)}
.tscale em{position:absolute;right:52px;bottom:0;font-style:normal;color:var(--amber);letter-spacing:.08em;white-space:nowrap}
.ov b{display:block;font-weight:500;letter-spacing:.14em;color:var(--amber);margin-bottom:3px}
.stage{width:100%;height:340px;border-radius:3px;background:linear-gradient(180deg,#0A1A2C,#06101B);display:block;touch-action:none;cursor:grab}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-family:var(--mono);font-size:10.5px;color:var(--mute);margin-top:8px}
.probes td{padding:5px 6px 5px 0}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{font-family:var(--mono);font-weight:500;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);text-align:left;padding:0 6px 7px 0;border-bottom:1px solid var(--line)}
td{padding:7px 6px 7px 0;border-bottom:1px solid #1B324F;vertical-align:middle;font-variant-numeric:tabular-nums}
td.num{font-family:var(--mono);text-align:right;white-space:nowrap}
td .st{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px;vertical-align:-1px}
.delta{font-family:var(--mono);font-size:11px;color:var(--mute)}
.chart{width:100%;height:auto;display:block}
.chart text{font-family:var(--mono);font-size:10px;fill:var(--mute)}
.chart .ax{stroke:var(--line);stroke-width:1}
.chart .gridl{stroke:#1B324F;stroke-width:1;stroke-dasharray:2 4}
pre.tree{font-family:var(--mono);font-size:11.5px;line-height:1.55;color:var(--cream);margin:0;white-space:pre;overflow-x:auto;background:var(--night);border-left:2px solid var(--amber);padding:10px 12px;border-radius:2px}
pre.tree .db{color:var(--amber)}
pre.tree .cm{color:var(--dim)}
.cams{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media (max-width:760px){.cams{grid-template-columns:1fr!important}}
.cam{position:relative;border-radius:3px;overflow:hidden;background:#000;aspect-ratio:16/9;max-width:100%}
.cam img{width:100%;height:100%;object-fit:cover;display:block;opacity:.92}
.cam .lab{position:absolute;left:8px;top:7px;font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--cream);background:rgba(6,16,27,.7);padding:3px 7px;border-radius:2px}
.cam.slot{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;border:1px dashed var(--line);background:var(--night)}
.cam.slot .lab{position:static;background:none;color:var(--amber)}
.cam .rec{position:absolute;right:8px;top:7px;font-family:var(--mono);font-size:10px;color:var(--amber);background:rgba(6,16,27,.7);padding:3px 7px;border-radius:2px}
.foot{margin-top:18px;padding-top:12px;border-top:1px solid var(--line);font-size:12px;color:var(--mute);max-width:72ch}
.foot b{color:var(--cream);font-weight:600}
.foot code{font-family:var(--mono);font-size:11px;color:var(--amber)}
button{font:inherit}
.btn{background:transparent;border:1px solid var(--line);color:var(--mute);border-radius:3px;padding:4px 10px;font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;cursor:pointer}
.btn:hover,.btn:focus-visible{border-color:var(--amber);color:var(--amber);outline:none}
.btn.on{border-color:var(--amber);color:var(--amber)}
.ctl{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-left:auto}
.ctl label{font-family:var(--mono);font-size:10.5px;color:var(--dim);letter-spacing:.06em}
input[type=range]{accent-color:var(--amber);width:120px}
</style>

<div class="wrap">
<header>
  <img src="__MARK__" alt="N50">
  <div class="hd-title"><b>North 50 Lab</b> &nbsp;·&nbsp; Fairbanks, Alaska &nbsp;·&nbsp; 64.86 N</div>
  <span class="pill live" id="pillWx">LIVE WEATHER</span>
  <span class="pill sim">SIMULATED SENSORS</span>
  <div class="clock" id="clock">--:--:-- AKDT</div>
</header>

<section class="grid g5" id="wx">
  <div class="panel tile"><h2>Outdoor air</h2><div class="v" id="wT">--<small>F</small></div><div class="s" id="wTs">Open-Meteo at the lab point, 1,204 ft</div><canvas class="spark" id="spT"></canvas></div>
  <div class="panel tile"><h2>Humidity</h2><div class="v" id="wH">--<small>%</small></div><div class="s" id="wHs">outdoor relative</div><canvas class="spark" id="spH"></canvas></div>
  <div class="panel tile"><h2>Dew point</h2><div class="v" id="wD">--<small>F</small></div><div class="s">outdoor, computed</div><canvas class="spark" id="spD"></canvas></div>
  <div class="panel tile"><h2>Wind</h2><div class="v" id="wW">--<small>mph</small></div><div class="s" id="wWs">calm</div><canvas class="spark" id="spW"></canvas></div>
  <div class="panel tile"><h2>Cloud</h2><div class="v" id="wC">--<small>%</small></div><div class="s" id="wCs">cover</div><canvas class="spark" id="spC"></canvas></div>
</section>

<section class="grid g5" id="wx2">
  <div class="panel tile"><h2>Sky</h2><div class="v" id="wSky">--</div><div class="s" id="wSkys">visibility</div></div>
  <div class="panel tile"><h2>Precip, 24 h</h2><div class="v" id="wP">--<small>in</small></div><div class="s" id="wPs">snow on ground</div></div>
  <div class="panel tile"><h2>Sun on the glass</h2><div class="v" id="wSol">--<small>W/m²</small></div><div class="s">shortwave, horizontal</div><canvas class="spark" id="spS"></canvas></div>
  <div class="panel tile"><h2>Mixed layer</h2><div class="v" id="wBL">--<small>ft</small></div><div class="s">boundary layer depth, model</div><canvas class="spark" id="spB"></canvas></div>
  <div class="panel tile"><h2>Fairbanks Intl, 430 ft</h2><div class="v" id="wApt">--<small>F</small></div><div class="s" id="wApts">valley reference</div></div>
</section>

<section class="panel ctlbar">
  <span class="kick">SIMULATION</span>
  <label for="tin">ROOM</label><input type="range" id="tin" min="60" max="78" value="70" step="1"><span class="delta" id="tinv">70 F</span>
  <label for="tout">OUTSIDE</label><input type="range" id="tout" min="-60" max="60" value="32" step="1"><span class="delta" id="toutv">live</span>
  <button class="btn" id="liveBtn" type="button">USE LIVE</button>
  <span class="sep"></span><label>VIEW</label><button class="btn on" id="vModel" type="button">GLASS</button><button class="btn" id="vTherm" type="button">ALL SURFACES</button>
  <span class="delta" style="margin-left:auto">drag a model to orbit</span>
</section>

<section class="grid g2 wall">
  <div class="panel">
    <h2>Vitro Wall <span class="tag">house · south elevation · camera "Vitro Wall"</span></h2>
    <div class="stagewrap"><canvas id="stageA" class="stage"></canvas><div class="tscale" id="tscaleA" hidden><span class="mx">--</span><i></i><span class="mn">--</span><em>SIMULATED · ε 0.95</em></div>
      <div class="ov"><b>VITRO WALL</b>3 × Vitro VIG 44 × 86 in, lower row<br>3 × transom 44 × 48 in, assumed<br>scaled off the 36 × 80 door</div></div>
  </div>
  <div class="panel">
    <h2>Vitro Wall probes <span class="tag">12 · two per lite on all six · pending Kevin</span></h2>
    <table class="probes" id="probesA"><thead><tr><th>Station</th><th>Lite</th><th style="text-align:right">Inboard</th><th style="text-align:right">Reading</th><th style="text-align:right">vs model</th></tr></thead><tbody></tbody></table>
  </div>
</section>

<section class="grid g2 wall">
  <div class="panel">
    <h2>LuxWall <span class="tag">lab · camera "LuxWall"</span></h2>
    <div class="stagewrap"><canvas id="stageB" class="stage"></canvas><div class="tscale" id="tscaleB" hidden><span class="mx">--</span><i></i><span class="mn">--</span><em>SIMULATED · ε 0.95</em></div>
      <div class="ov"><b>LUXWALL</b>3 openings in drywall<br>36 × 80 in, assumed, pending Kevin<br>spare LuxWall unit in opening 2</div></div>
  </div>
  <div class="panel">
    <h2>LuxWall probes <span class="tag">6 · two per lite · pending Kevin</span></h2>
    <table class="probes" id="probesB"><thead><tr><th>Station</th><th>Lite</th><th style="text-align:right">Inboard</th><th style="text-align:right">Reading</th><th style="text-align:right">vs model</th></tr></thead><tbody></tbody></table>
    <p class="delta" style="margin:10px 0 0">Two probes per lite, inside and outside, as Michael described. Kevin's schedule replaces all of this.</p>
  </div>
</section>

<section class="grid g2b">
  <div class="panel">
    <h2>Section trace, sight line inward <span class="tag">interior surface, F</span></h2>
    <svg class="chart" id="trace" viewBox="0 0 560 250" aria-label="Interior surface temperature from the sight line inward"></svg>
    <div class="legend"><span><i style="background:var(--amber)"></i>Vitro Wall probes</span><span><i style="background:var(--cream)"></i>LuxWall probes</span><span><i style="background:var(--mute)"></i>THERM model at today's outdoor temperature</span><span><i style="background:var(--cold)"></i>room dew point, 70 F at 40 percent</span></div>
  </div>
  <div class="panel">
    <h2>24 hours, sight line probe <span class="tag">F</span></h2>
    <svg class="chart" id="hist" viewBox="0 0 560 250" aria-label="Sight line probe over the last 24 hours"></svg>
    <div class="legend"><span><i style="background:var(--amber)"></i>sight line, interior</span><span><i style="background:var(--ice)"></i>seal, exterior</span><span><i style="background:var(--dim)"></i>outdoor air</span></div>
  </div>
</section>

<section class="panel">
  <h2>Seven days, the inversion tracker <span class="tag">lab on the slope at 1,204 ft against the valley at 430 ft</span></h2>
  <div class="grid g5" style="margin:0 0 12px">
    <div class="tile"><div class="s">Lab minus valley, now</div><div class="v" id="invNow">--<small>F</small></div><div class="s">positive means the lab sits above the cold pool</div></div>
    <div class="tile"><div class="s">Hours lab warmer, 7 d</div><div class="v" id="invHrs">--<small>h</small></div><div class="s" id="invPct">of 168</div></div>
    <div class="tile"><div class="s">Strongest, 7 d</div><div class="v" id="invMax">--<small>F</small></div><div class="s" id="invMaxT">--</div></div>
    <div class="tile"><div class="s">Aloft, 925 hPa minus lab</div><div class="v" id="invUp">--<small>F</small></div><div class="s">capping inversion check</div></div>
    <div class="tile"><div class="s">Coldest sight line, 7 d</div><div class="v" id="invCold">--<small>F</small></div><div class="s">simulated, at lab air temperature</div></div>
  </div>
  <svg class="chart" id="inv" viewBox="0 0 1120 260" aria-label="Seven day weather log with inversion bands"></svg>
  <div class="legend"><span><i style="background:var(--cream)"></i>lab air, 1,204 ft</span><span><i style="background:var(--dim)"></i>Fairbanks Intl, 430 ft</span><span><i style="background:var(--ice)"></i>air at 925 hPa, about 2,500 ft</span><span><i style="background:var(--amber)"></i>sight line probe, simulated</span><span><i style="background:#2b4a6b;border-radius:1px"></i>lab warmer than valley</span></div>
  <p class="delta" style="margin:12px 0 8px;max-width:80ch">The tracker: 14 real stations, October through March, against Fairbanks Intl at 430 ft. The curve saturates by about 850 ft and only on a slope. Creek bottoms behave like the valley floor whatever their height. The lab at 301 Henderson is on the slope at 1,204 ft, inside the NSGL terrain model, so it should run with the ridge stations, about 10 to 12 F warmer than the valley on an average winter day and 15 to 20 F warmer at minus 40. Fairbanks is in a surface inversion about 64 percent of winter hours. The 925 hPa line is the air above the pool.</p>
  <table class="probes" style="max-width:52rem"><thead><tr><th>Station</th><th style="text-align:right">Elev ft</th><th style="text-align:right">Mean</th><th style="text-align:right">Valley at −20</th><th style="text-align:right">Valley at −40</th><th style="text-align:right">% warmer</th></tr></thead><tbody>
  <tr><td>Goldstream Creek</td><td class="num">577</td><td class="num">−4.1</td><td class="num">−0.2</td><td class="num">+0.9</td><td class="num">24.9</td></tr>
  <tr><td>Ester village</td><td class="num">655</td><td class="num">−0.5</td><td class="num">+3.4</td><td class="num">+3.6</td><td class="num">46.5</td></tr>
  <tr><td>College 3NNW</td><td class="num">843</td><td class="num">+9.0</td><td class="num">+13.3</td><td class="num">+14.7</td><td class="num">87.7</td></tr>
  <tr><td>Gilmore Creek</td><td class="num">945</td><td class="num">+2.6</td><td class="num">+6.5</td><td class="num">+7.8</td><td class="num">62.5</td></tr>
  <tr><td>College 5NW</td><td class="num">978</td><td class="num">+9.1</td><td class="num">+14.0</td><td class="num">+14.6</td><td class="num">82.7</td></tr>
  <tr><td>Chena Ridge</td><td class="num">1,117</td><td class="num">+10.6</td><td class="num">+14.9</td><td class="num">+14.9</td><td class="num">86.5</td></tr>
  <tr><td>Fairbanks 11NE</td><td class="num">1,140</td><td class="num">+11.3</td><td class="num">+17.5</td><td class="num">+20.2</td><td class="num">85.5</td></tr>
  <tr style="color:var(--amber)"><td>N50 Lab, 301 Henderson, slope</td><td class="num">1,204</td><td class="num">no station</td><td class="num">expect +15</td><td class="num">expect +20</td><td class="num">—</td></tr>
  <tr><td>Keystone Ridge</td><td class="num">1,600</td><td class="num">+11.9</td><td class="num">+18.7</td><td class="num">+20.6</td><td class="num">83.7</td></tr>
  <tr><td>Ester Dome</td><td class="num">2,177</td><td class="num">+11.2</td><td class="num">+17.9</td><td class="num">+22.4</td><td class="num">80.7</td></tr>
  </tbody></table>
  <p class="delta" style="margin:8px 0 0">Source: EdgeRay THERM and climate handoff, 17 August 2026. Lab elevation from USGS 3DEP at the geocoded address, 1,203.5 ft, and 366 m from the NSGL 4 m terrain tile.</p>
</section>

<section class="grid g2b">
  <div class="panel">
    <h2>Lab network <span class="tag" id="netTag">UniFi, 5 Oct 17:22 · five Microedge PRECISE-LOG PL-TW thermocouple loggers, Modbus TCP</span></h2>
<pre class="tree" id="tree"></pre>
  </div>
  <div class="panel">
    <h2>Cameras <span class="tag">2 on the lab network</span></h2>
    <div class="cams">
      <div class="cam slot"><span class="lab">VITRO WALL</span><span class="delta">UniFi Protect · feed not connected</span></div>
      <div class="cam slot"><span class="lab">LUXWALL</span><span class="delta">UniFi Protect · feed not connected</span></div>
    </div>
  </div>
</section>

<p class="foot"><b>How the simulation works.</b> Weather is real: Open-Meteo at the lab's own coordinates and elevation, 1,204 ft, refreshed every 10 minutes and seven days back, plus the same model at Fairbanks Intl and the live airport observation for the valley reference. Probe readings are not real. Each station takes the fraction of the room-to-outdoor temperature difference that the N50 THERM model dropped at that point on 17 August (<code>−60 F</code> outside, <code>21 C</code> inside), and applies it to the outdoor temperature right now, plus a little sensor noise. The 24 hour history is built the same way from the last day of weather. The window banks are a Blender model. The Vitro Wall is three 44 by 86 inch units under three transoms, scaled off the door in the camera frame. The LuxWall openings are assumed at 36 by 80 inches. Every lite carries an inside and an outside Type T thermocouple. The loggers are Microedge PRECISE-LOG PL-TW, eight channels each, Modbus TCP on the lab network. The logger make, channel count, and the rest of the schedule are open questions to Kevin. The glass is always painted from the THERM model, edge coldest, and the all surfaces view extends that to frame and wall, so it is a prediction drawn as a camera frame, not a measurement. The camera panel is an empty slot until the UniFi feed is connected. When Kevin's loggers stream, these panels take the real numbers and the model line stays as the thing to beat.</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
<script>
// ---------- model ----------
// Field note, 17 Aug 2026. Predicted interior surface, F, at -60 F out / 69.8 F in. Station mm inboard of sight line.
const FN = [[0,46.3],[5,49.3],[12,52.2],[25,57.0],[50,61.0],[100,63.2],[150,63.5]];
const FRAC = FN.map(([mm,t]) => [mm, (69.8 - t) / (69.8 - (-60))]);   // share of delta-T dropped at the surface
const EXT_FRAC = 0.045;  // exterior face at the seal: THERM exterior trace, about 3 C above ambient at -60 F
function fracAt(mm){ // log-interp
  if(mm<=0) return FRAC[0][1]; if(mm>=150) return FRAC[FRAC.length-1][1];
  for(let i=1;i<FRAC.length;i++){ if(mm<=FRAC[i][0]){ const [a,fa]=FRAC[i-1],[b,fb]=FRAC[i]; const t=(Math.log(mm+1)-Math.log(a+1))/(Math.log(b+1)-Math.log(a+1)); return fa+(fb-fa)*t; } }
  return FRAC[FRAC.length-1][1];
}
function surf(mm, tin, tout){ return tin - fracAt(mm)*(tin-tout); }
function extFrac(mm){ const u=Math.min(1,Math.log(Math.max(0,mm)+1)/Math.log(151)); return 0.012 + (EXT_FRAC-0.012)*(1-u); }
function extSurf(tin, tout, mm){ return tout + extFrac(mm==null?150:mm)*(tin-tout); }
function dewF(tF, rh){ const c=(tF-32)*5/9, a=17.62,b=243.12, g=Math.log(rh/100)+a*c/(b+c); const d=b*g/(a-g); return d*9/5+32; }

// Probe stations. Assumed from the 2 Oct photographs: pink-tagged probes high and mid-glass on each lite, black probes at the mullion edge.
const PROBES = [
  {bank:"A", id:"A1-in",  mesh:"N50_A_P_unit1_in",  lite:"Vitro 1", mm:150, face:"in",  note:"Type T, interior, pink tag"},
  {bank:"A", id:"A1-out", mesh:"N50_A_P_unit1_out", lite:"Vitro 1", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"A", id:"A2-in",  mesh:"N50_A_P_unit2_in",  lite:"Vitro 2", mm:150, face:"in",  note:"Type T, interior, pink tag"},
  {bank:"A", id:"A2-out", mesh:"N50_A_P_unit2_out", lite:"Vitro 2", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"A", id:"A3-in",  mesh:"N50_A_P_unit3_in",  lite:"Vitro 3", mm:150, face:"in",  note:"Type T, interior, pink tag"},
  {bank:"A", id:"A3-out", mesh:"N50_A_P_unit3_out", lite:"Vitro 3", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"A", id:"T1-in",  mesh:"N50_A_P_transom1_in",  lite:"Transom 1", mm:150, face:"in",  note:"Type T, interior"},
  {bank:"A", id:"T1-out", mesh:"N50_A_P_transom1_out", lite:"Transom 1", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"A", id:"T2-in",  mesh:"N50_A_P_transom2_in",  lite:"Transom 2", mm:150, face:"in",  note:"Type T, interior"},
  {bank:"A", id:"T2-out", mesh:"N50_A_P_transom2_out", lite:"Transom 2", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"A", id:"T3-in",  mesh:"N50_A_P_transom3_in",  lite:"Transom 3", mm:150, face:"in",  note:"Type T, interior"},
  {bank:"A", id:"T3-out", mesh:"N50_A_P_transom3_out", lite:"Transom 3", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"B", id:"B1-in",  mesh:"N50_B_P_op1_in",  lite:"Opening 1", mm:150, face:"in",  note:"Type T, interior"},
  {bank:"B", id:"B1-out", mesh:"N50_B_P_op1_out", lite:"Opening 1", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"B", id:"B2-in",  mesh:"N50_B_P_op2_in",  lite:"LuxWall", mm:150, face:"in",  note:"Type T, interior"},
  {bank:"B", id:"B2-out", mesh:"N50_B_P_op2_out", lite:"LuxWall", mm:150, face:"out", note:"Type T, exterior"},
  {bank:"B", id:"B3-in",  mesh:"N50_B_P_op3_in",  lite:"Opening 3", mm:150, face:"in",  note:"Type T, interior"},
  {bank:"B", id:"B3-out", mesh:"N50_B_P_op3_out", lite:"Opening 3", mm:150, face:"out", note:"Type T, exterior"},
];
const noise = PROBES.map(()=>({v:0}));
function tick(dt){ noise.forEach(n=>{ n.v = n.v*0.96 + (Math.random()-0.5)*0.12; }); }
function readings(tin,tout){
  return PROBES.map((p,i)=> ({...p, t: (p.face==="out" ? extSurf(tin,tout,p.mm) : surf(p.mm,tin,tout)) + noise[i].v,
                               model: p.face==="out" ? extSurf(tin,tout,p.mm) : surf(p.mm,tin,tout)}));
}

// ---------- state ----------
const state = { tin:70, tout:32, live:true, wx:null, hourly:null, bank:"A", thermal:false };
const $ = id => document.getElementById(id);

// ---------- weather ----------
const LAB={lat:64.8654,lon:-147.9970,elev:367}, APT={lat:64.8154,lon:-147.8564,elev:132};
const HOURLY="temperature_2m,relative_humidity_2m,dew_point_2m,temperature_925hPa,temperature_850hPa,wind_speed_10m,wind_gusts_10m,cloud_cover,pressure_msl,precipitation,snowfall,snow_depth,visibility,weather_code,shortwave_radiation,boundary_layer_height";
const CURRENT="temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,cloud_cover,weather_code,visibility,precipitation,snowfall,shortwave_radiation";
async function fetchWx(){
  try{
    const u=`https://api.open-meteo.com/v1/forecast?latitude=${LAB.lat}&longitude=${LAB.lon}&elevation=${LAB.elev}&current=${CURRENT}&hourly=${HOURLY}&past_days=7&forecast_days=1&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FAnchorage`;
    const ua=`https://api.open-meteo.com/v1/forecast?latitude=${APT.lat}&longitude=${APT.lon}&elevation=${APT.elev}&current=temperature_2m,relative_humidity_2m&hourly=temperature_2m&past_days=7&forecast_days=1&temperature_unit=fahrenheit&timezone=America%2FAnchorage`;
    const [j,a]=await Promise.all([fetch(u).then(r=>r.json()), fetch(ua).then(r=>r.json())]);
    state.wx=j.current; state.hourly=j.hourly; state.apt={current:a.current,hourly:a.hourly};
    if(state.live){ state.tout=j.current.temperature_2m; $("tout").value=Math.round(state.tout); }
    $("pillWx").textContent="LIVE WEATHER "+j.current.time.slice(11,16)+" · LAB POINT, 1,204 FT";
    try{ const r=await fetch("https://api.weather.gov/stations/PAFA/observations/latest",{headers:{"Accept":"application/geo+json"}}); const pp=(await r.json()).properties;
      state.pafa={time:pp.timestamp,text:pp.textDescription,t:pp.temperature.value==null?null:pp.temperature.value*9/5+32,rh:pp.relativeHumidity.value,vis_m:pp.visibility.value}; }catch(e){ state.pafa=null; }
    renderWx(); update();
  }catch(e){ $("pillWx").textContent="WEATHER SAMPLE, "+SAMPLE.current.time.replace("T"," ")+" AK"; $("pillWx").classList.remove("live"); $("pillWx").classList.add("sim"); $("wTs").textContent="Open-Meteo sample, this page cannot fetch live"; if(!state.hourly) fakeHourly(); }
}
const SAMPLE = __SAMPLE__;
function fakeHourly(){ state.hourly=SAMPLE.hourly; state.wx=SAMPLE.current; state.apt=SAMPLE.apt; state.pafa=SAMPLE.pafa; if(state.live){ state.tout=state.wx.temperature_2m; $("tout").value=Math.round(state.tout); } renderWx(); update(); }
function dir(d){ return ["N","NE","E","SE","S","SW","W","NW"][Math.round(d/45)%8]; }
function renderWx(){
  const c=state.wx, h=state.hourly; if(!c) return;
  const idx = nowIdx(h);
  $("wT").innerHTML = c.temperature_2m.toFixed(1)+"<small>F</small>";
  $("wH").innerHTML = Math.round(c.relative_humidity_2m)+"<small>%</small>";
  $("wD").innerHTML = dewF(c.temperature_2m,c.relative_humidity_2m).toFixed(1)+"<small>F</small>";
  $("wW").innerHTML = c.wind_speed_10m.toFixed(1)+"<small>mph</small>";
  $("wWs").textContent = c.wind_speed_10m<1.5 ? "calm" : "from "+dir(c.wind_direction_10m);
  $("wC").innerHTML = Math.round(c.cloud_cover)+"<small>%</small>";
  $("wCs").textContent = c.cloud_cover>80?"overcast":c.cloud_cover>40?"partly cloudy":"clear, radiative night";
  const sl=(id,arr,col)=>spark($(id),arr.slice(Math.max(0,idx-23),idx+1),col);
  sl("spT",h.temperature_2m,"#EBB540"); sl("spH",h.relative_humidity_2m,"#9FD9E8");
  sl("spD",h.temperature_2m.map((t,i)=>dewF(t,h.relative_humidity_2m[i])),"#9FD9E8"); sl("spW",h.wind_speed_10m,"#9DB0C6"); sl("spC",h.cloud_cover,"#9DB0C6");
  const WMO={0:"clear",1:"mostly clear",2:"partly cloudy",3:"overcast",45:"fog",48:"rime fog",51:"drizzle",53:"drizzle",55:"drizzle",56:"freezing drizzle",57:"freezing drizzle",61:"rain",63:"rain",65:"heavy rain",66:"freezing rain",67:"freezing rain",71:"snow",73:"snow",75:"heavy snow",77:"snow grains",80:"showers",81:"showers",82:"showers",85:"snow showers",86:"snow showers",95:"thunder"};
  const visMi=(c.visibility!=null? c.visibility/5280 : null);
  let sky=WMO[c.weather_code]||"--"; if(visMi!=null && visMi<3 && c.relative_humidity_2m>=95 && c.weather_code<45) sky="fog or low cloud";
  $("wSky").textContent=sky; $("wSkys").textContent= visMi!=null ? "visibility "+visMi.toFixed(1)+" mi" : "visibility --";
  const p24=h.precipitation? h.precipitation.slice(Math.max(0,idx-23),idx+1).reduce((a,b)=>a+(b||0),0):null; const sd=h.snow_depth? h.snow_depth[idx]:null;
  $("wP").innerHTML=(p24==null?"--":p24.toFixed(2))+"<small>in</small>"; $("wPs").textContent= sd==null?"snow on ground --":"snow on ground "+(sd*12).toFixed(1)+" in";
  $("wSol").innerHTML=(c.shortwave_radiation==null?"--":Math.round(c.shortwave_radiation))+"<small>W/m²</small>";
  if(h.shortwave_radiation) sl("spS",h.shortwave_radiation,"#EBB540");
  const bl=h.boundary_layer_height? h.boundary_layer_height[idx]:null; $("wBL").innerHTML=(bl==null?"--":Math.round(bl))+"<small>ft</small>"; if(h.boundary_layer_height) sl("spB",h.boundary_layer_height,"#9FD9E8");
  const a=state.apt&&state.apt.current, pf=state.pafa; const at = pf&&pf.t!=null ? pf.t : (a? a.temperature_2m : null);
  $("wApt").innerHTML=(at==null?"--":at.toFixed(1))+"<small>F</small>";
  $("wApts").textContent= pf ? (pf.text||"")+" · observed "+pf.time.slice(11,16)+" UTC · lab "+(c.temperature_2m-at>=0?"+":"")+(c.temperature_2m-at).toFixed(1)+" F" : (a? "model cell · lab "+(c.temperature_2m-at>=0?"+":"")+(c.temperature_2m-at).toFixed(1)+" F" : "valley reference");
  renderHist(); renderInv();
}
function nowIdx(h){ const now = (state.hourly===SAMPLE) ? new Date(SAMPLE.current.time+":00") : new Date(); let best=0,bd=1e18; h.time.forEach((t,i)=>{ const d=Math.abs(new Date(t+(t.length===16?":00":""))-now); if(d<bd){bd=d;best=i;} }); return best; }
function spark(cv,arr,col){
  const dpr=devicePixelRatio||1, W=cv.clientWidth, H=cv.clientHeight; cv.width=W*dpr; cv.height=H*dpr; const g=cv.getContext("2d"); g.scale(dpr,dpr);
  const mn=Math.min(...arr), mx=Math.max(...arr), sp=(mx-mn)||1; const X=i=>i/(arr.length-1)*(W-2)+1, Y=v=>H-3-(v-mn)/sp*(H-8);
  g.beginPath(); arr.forEach((v,i)=> i?g.lineTo(X(i),Y(v)):g.moveTo(X(i),Y(v))); g.lineTo(X(arr.length-1),H); g.lineTo(X(0),H); g.closePath(); g.fillStyle=col+"22"; g.fill();
  g.beginPath(); arr.forEach((v,i)=> i?g.lineTo(X(i),Y(v)):g.moveTo(X(i),Y(v))); g.strokeStyle=col; g.lineWidth=1.4; g.stroke();
  g.beginPath(); g.arc(X(arr.length-1),Y(arr[arr.length-1]),2.4,0,7); g.fillStyle=col; g.fill();
}

// ---------- probe table ----------
function colorFor(t,tin,tout){ // cold -> ember
  const lo=Math.min(tout,tin), f=Math.max(0,Math.min(1,(t-lo)/((tin-lo)||1)));
  const a=[79,163,199], b=[244,184,96]; const c=a.map((x,i)=>Math.round(x+(b[i]-x)*f)); return `rgb(${c[0]},${c[1]},${c[2]})`;
}
function renderTable(rs){ ["A","B"].forEach(b=>{
  const tb=$("probes"+b).querySelector("tbody"); tb.innerHTML="";
  rs.filter(r=>r.bank===b).forEach(r=>{ const d=r.t-r.model; const tr=document.createElement("tr");
    tr.innerHTML=`<td><span class="st" style="background:${r.face==="out"?"#9FD9E8":colorFor(r.t,state.tin,state.tout)}"></span>${r.id}<div class="delta">${r.note}</div></td><td>${r.lite}</td><td class="num">${r.face==="out"?"ext":r.mm+" mm"}</td><td class="num" style="color:var(--cream)">${r.t.toFixed(1)} F</td><td class="num"><span class="delta">${d>=0?"+":""}${d.toFixed(2)}</span></td>`;
    tb.appendChild(tr); }); });
}

// ---------- section trace ----------
function renderTrace(rs){
  const svg=$("trace"); const W=560,H=250, L=44,R=14,T=16,B=34; const tin=state.tin,tout=state.tout;
  const mmX = mm => L + (Math.log(mm+1)/Math.log(151))*(W-L-R);
  const ys = [tin, Math.min(tout, tin-30)]; const ymax=Math.ceil(tin/5)*5+5, ymin=Math.floor(Math.min(ys[1], surf(0,tin,tout)-5)/10)*10;
  const Y=v=>T+(ymax-v)/(ymax-ymin)*(H-T-B);
  let s="";
  for(let v=ymin; v<=ymax; v+=10){ s+=`<line class="gridl" x1="${L}" x2="${W-R}" y1="${Y(v)}" y2="${Y(v)}"/><text x="${L-6}" y="${Y(v)+3}" text-anchor="end">${v}</text>`; }
  [0,5,12,25,50,100,150].forEach(mm=>{ s+=`<line class="ax" x1="${mmX(mm)}" x2="${mmX(mm)}" y1="${H-B}" y2="${H-B+4}"/><text x="${mmX(mm)}" y="${H-B+15}" text-anchor="middle">${mm}</text>`; });
  s+=`<text x="${(L+W-R)/2}" y="${H-4}" text-anchor="middle">mm inboard of sight line, log scale</text>`;
  s+=`<line class="ax" x1="${L}" x2="${W-R}" y1="${H-B}" y2="${H-B}"/>`;
  // dew point of room air 70F / 40%
  const dp=dewF(70,40); s+=`<line x1="${L}" x2="${W-R}" y1="${Y(dp)}" y2="${Y(dp)}" stroke="#4FA3C7" stroke-dasharray="4 4"/><text x="${W-R}" y="${Y(dp)-4}" text-anchor="end" fill="#4FA3C7">dew ${dp.toFixed(0)} F</text>`;
  // model curve
  let d=""; for(let mm=0; mm<=150; mm+=1){ d+=(mm?"L":"M")+mmX(mm).toFixed(1)+" "+Y(surf(mm,tin,tout)).toFixed(1)+" "; }
  s+=`<path d="${d}" fill="none" stroke="#9DB0C6" stroke-width="1.6"/>`;
  // probes
  rs.filter(r=>r.face==="in").forEach(r=>{ s+= r.bank==="A" ? `<circle cx="${mmX(r.mm)}" cy="${Y(r.t)}" r="4.5" fill="#EBB540" stroke="#06101B" stroke-width="1.5"/>` : `<rect x="${mmX(r.mm)-4}" y="${Y(r.t)-4}" width="8" height="8" fill="#F5F2EA" stroke="#06101B" stroke-width="1.5"/>`; });
  s+=`<text x="${L+4}" y="${T+10}" fill="#F5F2EA">room ${tin} F · outside ${tout.toFixed(0)} F</text>`;
  svg.innerHTML=s;
}

// ---------- 24h history ----------
function renderHist(){
  const h=state.hourly; if(!h) return; const idx=nowIdx(h); const i0=Math.max(0,idx-23);
  const svg=$("hist"); const W=560,H=250,L=44,R=14,T=16,B=34; const tin=state.tin;
  const to=h.temperature_2m.slice(i0,idx+1), sl=to.map(t=>surf(0,tin,t)), ex=to.map(t=>extSurf(tin,t));
  const all=[...to,...sl,...ex]; const ymax=Math.ceil(Math.max(...all)/10)*10+5, ymin=Math.floor(Math.min(...all)/10)*10-5;
  const X=i=>L+i/(to.length-1)*(W-L-R), Y=v=>T+(ymax-v)/(ymax-ymin)*(H-T-B);
  let s=""; for(let v=ymin;v<=ymax;v+=10){ s+=`<line class="gridl" x1="${L}" x2="${W-R}" y1="${Y(v)}" y2="${Y(v)}"/><text x="${L-6}" y="${Y(v)+3}" text-anchor="end">${v}</text>`; }
  for(let i=0;i<to.length;i+=6){ const tm=h.time[i0+i].slice(11,16); s+=`<text x="${X(i)}" y="${H-B+15}" text-anchor="middle">${tm}</text>`; }
  s+=`<line class="ax" x1="${L}" x2="${W-R}" y1="${H-B}" y2="${H-B}"/>`;
  const path=(arr,col,w)=>{ let d=""; arr.forEach((v,i)=>d+=(i?"L":"M")+X(i).toFixed(1)+" "+Y(v).toFixed(1)+" "); return `<path d="${d}" fill="none" stroke="${col}" stroke-width="${w}"/>`; };
  s+=path(to,"#5E7490",1.2)+path(ex,"#9FD9E8",1.4)+path(sl,"#EBB540",1.8);
  s+=`<circle cx="${X(to.length-1)}" cy="${Y(sl[sl.length-1])}" r="3.5" fill="#EBB540"/>`;
  svg.innerHTML=s;
}

// ---------- network tree ----------
const LOG=[["PL060300603…0f:2c",-48],["PL06030060…18:30",-51],["PL06030060…20:c4",-53],["PL06030060…20:e0",-49],["PL06030060…2d:bc",-50]];
function renderInv(){
  const h=state.hourly; if(!h) return; const idx=nowIdx(h); const i0=Math.max(0,idx-167);
  const to=h.temperature_2m.slice(i0,idx+1), sl=to.map(t=>surf(0,state.tin,t));
  const up=(h.temperature_925hPa||to).slice(i0,idx+1).map((v,i)=>v==null?to[i]:v);
  const ah=state.apt&&state.apt.hourly; let val=to.map(()=>null);
  if(ah){ const m=new Map(ah.time.map((t,i)=>[t,ah.temperature_2m[i]])); val=h.time.slice(i0,idx+1).map((t,i)=>{ const v=m.get(t); return v==null?to[i]:v; }); }
  const inv=to.map((t,i)=>t-val[i]);
  const hrs=inv.filter(v=>v>0.5).length; let mx=-99,mi=0; inv.forEach((v,i)=>{ if(v>mx){mx=v;mi=i;} });
  const now=inv[inv.length-1]; $("invNow").innerHTML=(now>=0?"+":"")+now.toFixed(1)+"<small>F</small>";
  $("invHrs").innerHTML=hrs+"<small>h</small>"; $("invPct").textContent=Math.round(100*hrs/inv.length)+" percent of "+inv.length;
  $("invMax").innerHTML=(mx>=0?"+":"")+mx.toFixed(1)+"<small>F</small>"; $("invMaxT").textContent=h.time[i0+mi].replace("T"," ");
  const upn=up[up.length-1]-to[to.length-1]; $("invUp").innerHTML=(upn>=0?"+":"")+upn.toFixed(1)+"<small>F</small>";
  $("invCold").innerHTML=Math.min(...sl).toFixed(1)+"<small>F</small>";
  const svg=$("inv"); const W=1120,H=260,L=44,R=14,T=14,B=34;
  const all=[...to,...up,...sl,...val]; const ymax=Math.ceil(Math.max(...all)/10)*10+5, ymin=Math.floor(Math.min(...all)/10)*10-5;
  const X=i=>L+i/(to.length-1)*(W-L-R), Y=v=>T+(ymax-v)/(ymax-ymin)*(H-T-B);
  let s="";
  let run=null; inv.forEach((v,i)=>{ if(v>0.5&&run===null) run=i; if((v<=0.5||i===inv.length-1)&&run!==null){ const e=(v<=0.5)?i:i+1; s+=`<rect x="${X(run)}" y="${T}" width="${Math.max(1,X(Math.min(e,inv.length-1))-X(run))}" height="${H-T-B}" fill="#2b4a6b" opacity=".45"/>`; run=null; } });
  for(let v=ymin;v<=ymax;v+=10){ s+=`<line class="gridl" x1="${L}" x2="${W-R}" y1="${Y(v)}" y2="${Y(v)}"/><text x="${L-6}" y="${Y(v)+3}" text-anchor="end">${v}</text>`; }
  for(let i=0;i<to.length;i++){ const t=h.time[i0+i]; if(t.endsWith("T00:00")){ s+=`<line class="ax" x1="${X(i)}" x2="${X(i)}" y1="${H-B}" y2="${H-B+4}"/><text x="${X(i)}" y="${H-B+15}" text-anchor="middle">${t.slice(5,10)}</text>`; } }
  s+=`<line class="ax" x1="${L}" x2="${W-R}" y1="${H-B}" y2="${H-B}"/>`;
  const path=(arr,col,w)=>{ let d=""; arr.forEach((v,i)=>d+=(i?"L":"M")+X(i).toFixed(1)+" "+Y(v).toFixed(1)+" "); return `<path d="${d}" fill="none" stroke="${col}" stroke-width="${w}"/>`; };
  s+=path(val,"#5E7490",1.2)+path(up,"#9FD9E8",1.1)+path(to,"#F5F2EA",1.4)+path(sl,"#EBB540",1.6);
  s+=`<circle cx="${X(to.length-1)}" cy="${Y(sl[sl.length-1])}" r="3.5" fill="#EBB540"/>`;
  svg.innerHTML=s;
}
function renderTree(){
  const j=()=> (Math.random()<0.15? (Math.random()<0.5?-1:1):0);
  const L=LOG.map(([n,d],i)=>`│   ${i<4?"├──":"└──"} ${n.padEnd(22)} <span class="db">${d+j()} dBm</span> <span class="cm">PL-TW, 8 ch, Type T</span>`).join("\n");
  $("tree").innerHTML=`Starlink
└── North 50 Lab <span class="cm">(gateway)</span>
    └── N50 Main Switch
        ├── House AP
        ├── Vitro Wall          <span class="cm">(camera)</span>
        ├── Lab AC Pro          <span class="cm">(access point)</span>
${L}
        └── LuxWall             <span class="cm">(camera)</span>`;
}

// ---------- 3D walls, Blender model, one viewer per wall ----------
const viewers={};
const BANKS = { A:{center:[0,2.3,0], dist:7.6}, B:{center:[9,1.7,0], dist:7.2} };
function initViewer(bank){
  if(!window.THREE || !THREE.GLTFLoader) return;
  const cv=$("stage"+bank); const W=cv.clientWidth,H=cv.clientHeight;
  const renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:true}); renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setSize(W,H,false);
  renderer.outputEncoding=THREE.sRGBEncoding;
  const scene=new THREE.Scene();
  const cam=new THREE.PerspectiveCamera(30,W/H,0.1,100);
  scene.add(new THREE.HemisphereLight(0xe8eef7,0x0a1a2c,1.0)); const dl=new THREE.DirectionalLight(0xfff1d6,0.9); dl.position.set(3,6,8); scene.add(dl);
  const pm={}; const other = bank==="A" ? /^N50_B_/ : /^N50_A_/;
  new THREE.GLTFLoader().load("__GLB__", g=>{
    scene.add(g.scene); g.scene.updateMatrixWorld(true);
    g.scene.traverse(o=>{ const key=(o.name||"").replace(/\.\d+$/,""); if(other.test(key)) o.visible=false;
      if(o.isMesh){ const k2=(o.name||(o.parent&&o.parent.name)||"").replace(/\.\d+$/,""); if(/^N50_[AB]_P_/.test(k2)){ o.material=o.material.clone(); pm[k2]=o; } if(o.material&&o.material.transparent){ o.material.depthWrite=false; } } });
    // glass planes for the thermal view: subdivided, vertex colored from the THERM curve
    const glass=[]; const orig=new Map();
    g.scene.traverse(o=>{ if(!o.isMesh) return; const k=(o.name||(o.parent&&o.parent.name)||"").replace(/\.\d+$/,""); if(other.test(k)) return;
      orig.set(o,o.material);
      if(/^N50_[AB]_(vitro|transom|glass)_[0-9]/.test(k)){ const bb=new THREE.Box3().setFromObject(o); const sz=new THREE.Vector3(); bb.getSize(sz); const ctr=new THREE.Vector3(); bb.getCenter(ctr);
        [["in", 0.013],["out",-0.013]].forEach(([face,dz])=>{ const geo=new THREE.PlaneGeometry(sz.x,sz.y,36,56); const col=new Float32Array(geo.attributes.position.count*3); geo.setAttribute("color",new THREE.BufferAttribute(col,3));
          const m=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide})); m.position.set(ctr.x,ctr.y,ctr.z+dz); m.visible=true; m.userData={w:sz.x,h:sz.y,face}; scene.add(m); glass.push(m); }); } });
    viewers[bank].pm=pm; viewers[bank].glass=glass; viewers[bank].orig=orig; viewers[bank].scene=g.scene; update();
  }, undefined, e=>console.error("glb",e));
  let rx=0.06, ry=-0.25, drag=false, lx=0, ly=0, auto=true, t0=performance.now()+(bank==="B"?4000:0);
  cv.addEventListener("pointerdown",e=>{drag=true;auto=false;lx=e.clientX;ly=e.clientY;cv.setPointerCapture(e.pointerId);cv.style.cursor="grabbing";});
  cv.addEventListener("pointermove",e=>{ if(!drag) return; ry+=(e.clientX-lx)*0.008; rx+=(e.clientY-ly)*0.006; rx=Math.max(-0.4,Math.min(0.6,rx)); lx=e.clientX; ly=e.clientY; });
  cv.addEventListener("pointerup",()=>{drag=false;cv.style.cursor="grab";});
  const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
  function frame(){
    const b=BANKS[bank], c=b.center, d=b.dist*Math.max(1,1.55/cam.aspect);
    if(auto&&!reduce){ const t=(performance.now()-t0)/1000; ry=-0.25+0.2*Math.sin(t*0.25); }
    cam.position.set(c[0]+d*Math.sin(ry)*Math.cos(rx), c[1]+d*Math.sin(rx), c[2]+d*Math.cos(ry)*Math.cos(rx)); cam.lookAt(c[0],c[1],c[2]);
    renderer.render(scene,cam); requestAnimationFrame(frame); }
  frame();
  addEventListener("resize",()=>{ const W=cv.clientWidth,H=cv.clientHeight; renderer.setSize(W,H,false); cam.aspect=W/H; cam.updateProjectionMatrix(); });
  viewers[bank]={pm:null};
}
function initThree(){ initViewer("A"); initViewer("B"); }
// ironbow palette, t normalised 0..1
const IRON=[[0,0,0],[26,2,56],[138,10,110],[232,50,28],[255,154,31],[255,229,107],[255,255,255]];
function iron(u){ u=Math.max(0,Math.min(1,u)); const k=u*(IRON.length-1), i=Math.floor(k), f=k-i, a=IRON[i], b=IRON[Math.min(i+1,IRON.length-1)]; return [a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f].map(v=>v/255); }
function thermalRange(){ const lo=Math.min(state.tout, surf(0,state.tin,state.tout))-3, hi=state.tin+2; return [lo,hi]; }
function applyThermal(){
  const [lo,hi]=thermalRange(); const n=v=>(v-lo)/(hi-lo);
  ["A","B"].forEach(b=>{ const v=viewers[b]; if(!v||!v.scene) return;
    $("tscale"+b).hidden=false; $("tscale"+b).querySelector(".mx").textContent=hi.toFixed(1); $("tscale"+b).querySelector(".mn").textContent=lo.toFixed(1);
    v.scene.traverse(o=>{ if(!o.isMesh) return; const k=(o.name||(o.parent&&o.parent.name)||"").replace(/\.\d+$/,"");
      if(!state.thermal){ if(v.orig.has(o)) o.material=v.orig.get(o); return; }
      if(/_P_/.test(k)) return;
      // walls and frames: grade from the outdoor face to the room face through the thickness, so reveals show the gradient
      const isFrame=/_(mull|head|sill|transom_bar|jamb)/.test(k);
      const tIn = isFrame ? surf(6,state.tin,state.tout)-1.5 : state.tin-1.2;
      const tOut = state.tout + (isFrame?0.06:0.03)*(state.tin-state.tout);
      const g=o.geometry; if(!g.attributes.color){ g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(g.attributes.position.count*3),3)); }
      g.computeBoundingBox(); const bb=g.boundingBox; const pos=g.attributes.position, col=g.attributes.color;
      // local z runs outdoor (min) to room (max) for every box in this model
      for(let i=0;i<pos.count;i++){ const u=(pos.getZ(i)-bb.min.z)/((bb.max.z-bb.min.z)||1); const t=tOut+(tIn-tOut)*u; const c=iron(n(t)); col.setXYZ(i,c[0],c[1],c[2]); }
      col.needsUpdate=true;
      if(!o.userData.tm) o.userData.tm=new THREE.MeshBasicMaterial({vertexColors:true}); o.material=o.userData.tm; });
    v.glass.forEach(m=>{ m.visible=true; const pos=m.geometry.attributes.position, col=m.geometry.attributes.color, w=m.userData.w, h=m.userData.h;
      for(let i=0;i<pos.count;i++){ const x=pos.getX(i), y=pos.getY(i); const mm=Math.max(0,Math.min(w/2-Math.abs(x), h/2-Math.abs(y))*1000); const t=m.userData.face==="out" ? extSurf(state.tin,state.tout,mm) : surf(mm,state.tin,state.tout); const c=iron(n(t)); col.setXYZ(i,c[0],c[1],c[2]); } col.needsUpdate=true; });
  });
}
function setView(th){ state.thermal=th; $("vModel").classList.toggle("on",!th); $("vTherm").classList.toggle("on",th); update(); }
function paintProbes(rs){ rs.forEach(r=>{ const v=viewers[r.bank]; if(!v||!v.pm) return; const m=v.pm[r.mesh]; if(!m) return; if(r.face==="out"){ m.material.color.set(0x9fd9e8); m.material.emissive.set(0x0f3040); return; } const c=new THREE.Color(colorFor(r.t,state.tin,state.tout)); m.material.color.copy(c); m.material.emissive.copy(c).multiplyScalar(.3); }); }
// ---------- loop ----------
function update(){ tick(); const rs=readings(state.tin,state.tout); renderTable(rs); renderTrace(rs); paintProbes(rs); applyThermal(); }
$("tin").addEventListener("input",e=>{ state.tin=+e.target.value; $("tinv").textContent=state.tin+" F"; update(); renderHist(); renderInv(); });
$("tout").addEventListener("input",e=>{ state.tout=+e.target.value; state.live=false; $("toutv").textContent=state.tout+" F"; $("liveBtn").classList.remove("on"); update(); });
$("liveBtn").addEventListener("click",()=>{ state.live=true; $("liveBtn").classList.add("on");
$("vModel").addEventListener("click",()=>setView(false)); $("vTherm").addEventListener("click",()=>setView(true)); if(state.wx){ state.tout=state.wx.temperature_2m; $("tout").value=Math.round(state.tout); } $("toutv").textContent="live"; update(); });
$("liveBtn").classList.add("on");
$("vModel").addEventListener("click",()=>setView(false)); $("vTherm").addEventListener("click",()=>setView(true));
function clock(){ const d=new Date(); $("clock").textContent=d.toLocaleTimeString("en-US",{timeZone:"America/Anchorage",hour12:false})+" AK"; }
setInterval(clock,1000); clock();
renderTree(); setInterval(renderTree,4000);
initThree(); update(); setInterval(update,2000);
fetchWx(); setInterval(fetchWx,600000);
</script>
"""
HTML = HTML.replace("__SAMPLE__", open(f"{S}/wx_sample_min.json").read()).replace("__MARK__", MARK).replace("__CAMH__", CAM_H).replace("__CAML__", CAM_L).replace("__GLB__", GLB).replace("__IR1__", IR1).replace("__IR2__", IR2)
out = f"{S}/n50_lab_live.html"; open(out, "w").write(HTML); print("wrote", out, len(HTML)//1024, "KB")
local = "/Users/michaelweinfeld/Documents/2026/N50/reports/Field Report 01 - Window Sensors/N50_Lab_Live_local.html"
open(local, "w").write("<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body>" + HTML + "</body></html>"); print("local copy written")
