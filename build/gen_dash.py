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
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
.g2{grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)}
.g2b{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
@media (max-width:900px){.g3,.g5{grid-template-columns:repeat(2,minmax(0,1fr))}.g2,.g2b{grid-template-columns:1fr}}
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
.sb{font-family:var(--mono);font-size:16px;letter-spacing:.14em;color:var(--amber);padding:10px 0}
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
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
  <span class="pill live" id="pillWx" style="display:none">LIVE WEATHER</span>
  <span class="pill sim" id="pillSim">CONNECTING TO LAB</span>
  <div class="clock" id="clock">--:--:-- AKDT</div>
</header>
<div class="mono" style="margin:14px 0 20px;font-size:12px;letter-spacing:.06em;color:#9DB0C6"><b style="color:#EBB540">N50 QUALIFIED</b> &nbsp;·&nbsp; testing vacuum insulated glass integrations in Alaska's proving ground</div>

<section class="grid g3" id="wx">
  <div class="panel tile"><h2>Outdoor air</h2><div class="v" id="wT">--<small>F</small></div><div class="s" id="wTs">lab outside probes</div><canvas class="spark" id="spT" style="display:none"></canvas></div>
  <div class="panel tile"><h2>Inside air</h2><div class="v" id="wIn">--<small>F</small></div><div class="s" id="wIns">lab inside probes</div></div>
  <div class="panel tile"><h2>Fairbanks Intl, 430 ft</h2><div class="v" id="wApt">--<small>F</small></div><div class="s" id="wApts">valley reference</div></div>
</section>
<div hidden>
  <div class="panel tile"><h2>NSGL resort, estimated</h2><div class="v" id="wN">--<small>F</small></div><div class="s" id="wNs">waiting for data</div></div>
  <div class="panel tile"><h2>Humidity</h2><div class="v" id="wH">--<small>%</small></div><div class="s" id="wHs">outdoor relative</div><canvas class="spark" id="spH"></canvas></div>
  <div class="panel tile"><h2>Dew point</h2><div class="v" id="wD">--<small>F</small></div><div class="s">outdoor, computed</div><canvas class="spark" id="spD"></canvas></div>
  <div class="panel tile"><h2>Wind</h2><div class="v" id="wW">--<small>mph</small></div><div class="s" id="wWs">calm</div><canvas class="spark" id="spW"></canvas></div>
  <div class="panel tile"><h2>Cloud</h2><div class="v" id="wC">--<small>%</small></div><div class="s" id="wCs">cover</div><canvas class="spark" id="spC"></canvas></div>
  <div class="panel tile"><h2>Sky</h2><div class="v" id="wSky">--</div><div class="s" id="wSkys">visibility</div></div>
  <div class="panel tile"><h2>Precip, 24 h</h2><div class="v" id="wP">--<small>in</small></div><div class="s" id="wPs">snow on ground</div></div>
  <div class="panel tile"><h2>Sun on the glass</h2><div class="v" id="wSol">--<small>W/m²</small></div><div class="s">shortwave, horizontal</div><canvas class="spark" id="spS"></canvas></div>
  <div class="panel tile"><h2>Mixed layer</h2><div class="v" id="wBL">--<small>ft</small></div><div class="s">boundary layer depth, model</div><canvas class="spark" id="spB"></canvas></div>
</div>

<section class="panel ctlbar">
  <span class="kick" style="display:none">SIMULATION</span>
  <span style="display:none"><label for="tin">ROOM</label><input type="range" id="tin" min="60" max="78" value="70" step="1"><span class="delta" id="tinv">70 F</span></span>
  <span style="display:none"><label for="tout">OUTSIDE</label><input type="range" id="tout" min="-60" max="60" value="32" step="1"><span class="delta" id="toutv">live</span></span>
  <button class="btn" id="liveBtn" type="button" style="display:none">USE LIVE</button>
  <span class="sep"></span><label>VIEW</label><button class="btn on" id="vModel" type="button">GLASS</button><button class="btn" id="vTherm" type="button">ALL SURFACES</button>
  <span class="delta" style="margin-left:auto">drag a model to orbit</span>
</section>

<section class="grid g2 wall">
  <div class="panel">
    <h2>V Wall <span class="tag">three lites · V1 to V3 left to right</span></h2>
    <div class="stagewrap"><canvas id="stageA" class="stage"></canvas><div class="tscale" id="tscaleA" hidden><span class="mx">--</span><i></i><span class="mn">--</span><em>NO LIVE DATA</em></div>
      <div class="ov"><b>V WALL</b>V1 VIG in · V2 no second layer · V3 VIG out<br>three openings, 36 × 80 in assumed</div></div>
  </div>
  <div class="panel">
    <h2>V Wall probes <span class="tag">11 probes</span></h2>
    <table class="probes" id="probesA"><thead><tr><th>Station</th><th>Lite</th><th style="text-align:right">Inboard</th><th style="text-align:right">Reading</th></tr></thead><tbody></tbody></table>
  </div>
</section>

<section class="grid g2 wall">
  <div class="panel">
    <h2>L Wall <span class="tag">six lites in one frame · L1 to L6</span></h2>
    <div class="stagewrap"><canvas id="stageB" class="stage"></canvas><div class="tscale" id="tscaleB" hidden><span class="mx">--</span><i></i><span class="mn">--</span><em>NO LIVE DATA</em></div>
      <div class="ov"><b>L WALL</b>six lites in one frame, L1 to L6<br>lower 44 × 86 in, upper 44 × 48 in assumed<br>top L3 L2 L1 · bottom L6 L5 L4, from inside</div></div>
  </div>
  <div class="panel">
    <h2>L Wall probes <span class="tag">20 probes</span></h2>
    <table class="probes" id="probesB"><thead><tr><th>Station</th><th>Lite</th><th style="text-align:right">Inboard</th><th style="text-align:right">Reading</th></tr></thead><tbody></tbody></table>
    <p class="delta" style="margin:10px 0 0">On each lite: centre of glass inside, edge of glass inside and centre of glass outside on each lite, plus one inside and one outside air thermocouple per wall. Every reading is live from the lab loggers. A dash means no reading yet.</p>
  </div>
</section>

<section class="grid g2b" id="comfort">
  <div class="panel" style="grid-column:1/-1">
    <h2>C Series <span class="tag">comfort sensors</span> <span class="tag" id="cState">standby · 3 sensors linked</span></h2>
    <div class="cgrid" id="cGrid"><div class="tile" id="c1"><div class="s">C1</div><div class="v sb">STANDBY</div><div class="s">linked · awaiting first sample</div></div><div class="tile" id="c2"><div class="s">C2</div><div class="v sb">STANDBY</div><div class="s">linked · awaiting first sample</div></div><div class="tile" id="c3"><div class="s">C3</div><div class="v sb">STANDBY</div><div class="s">linked · awaiting first sample</div></div></div>
  </div>
</section>

<section class="grid g2b">
  <div class="panel" style="grid-column:1/-1">
    <h2>Cameras <span class="tag">V Wall and L Wall</span></h2>
    <div class="cams">
      <div class="cam slot"><span class="lab">V WALL</span><span class="delta">live stream coming</span></div>
      <div class="cam slot"><span class="lab">L WALL</span><span class="delta">live stream coming</span></div>
    </div>
  </div>
</section>

<p class="foot"><b>About this page.</b> N50 Qualified: testing vacuum insulated glass integrations in Alaska's proving ground. Two test walls at the North 50 lab in Fairbanks: V Wall, three lites, and L Wall, six lites in one frame. Every lite carries a thermocouple at the centre of glass inside and out and one at the edge of glass inside, and each wall has an inside and an outside air thermocouple, 31 in all, read every 15 minutes. Every number on this page is measured: the lab probes, and the National Weather Service observation at Fairbanks Intl as the valley reference. The NSGL estimate is the lab's own outside air, since the lodge sits within about 23 ft of the lab's elevation. In the 3D view the glass is painted from the live probes; frames and walls are estimated, since nothing is mounted on them. The 3D walls are drawn to scale from the camera views.</p>
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
  {bank:"A", id:"V1 ci", mesh:"N50_A_P_V1_ci", lite:"V1 · VIG in", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"A", id:"V1 ce", mesh:"N50_A_P_V1_ce", lite:"V1 · VIG in", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"A", id:"V1 ei", mesh:"N50_A_P_V1_ei", lite:"V1 · VIG in", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"A", id:"V2 ci", mesh:"N50_A_P_V2_ci", lite:"V2 · no second layer", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"A", id:"V2 ce", mesh:"N50_A_P_V2_ce", lite:"V2 · no second layer", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"A", id:"V2 ei", mesh:"N50_A_P_V2_ei", lite:"V2 · no second layer", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"A", id:"V3 ci", mesh:"N50_A_P_V3_ci", lite:"V3 · VIG out", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"A", id:"V3 ce", mesh:"N50_A_P_V3_ce", lite:"V3 · VIG out", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"A", id:"V3 ei", mesh:"N50_A_P_V3_ei", lite:"V3 · VIG out", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"A", id:"air in 1", mesh:"N50_A_P_air_in1", lite:"room", mm:0, face:"in", note:"interior ambient air", kind:"air"},
  {bank:"A", id:"air out 1", mesh:"N50_A_P_air_out1", lite:"outside", mm:0, face:"out", note:"exterior ambient air", kind:"air"},
  {bank:"B", id:"L1 ci", mesh:"N50_B_P_L1_ci", lite:"L1", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"B", id:"L1 ce", mesh:"N50_B_P_L1_ce", lite:"L1", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"B", id:"L1 ei", mesh:"N50_B_P_L1_ei", lite:"L1", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"B", id:"L2 ci", mesh:"N50_B_P_L2_ci", lite:"L2", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"B", id:"L2 ce", mesh:"N50_B_P_L2_ce", lite:"L2", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"B", id:"L2 ei", mesh:"N50_B_P_L2_ei", lite:"L2", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"B", id:"L3 ci", mesh:"N50_B_P_L3_ci", lite:"L3", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"B", id:"L3 ce", mesh:"N50_B_P_L3_ce", lite:"L3", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"B", id:"L3 ei", mesh:"N50_B_P_L3_ei", lite:"L3", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"B", id:"L4 ci", mesh:"N50_B_P_L4_ci", lite:"L4", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"B", id:"L4 ce", mesh:"N50_B_P_L4_ce", lite:"L4", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"B", id:"L4 ei", mesh:"N50_B_P_L4_ei", lite:"L4", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"B", id:"L5 ci", mesh:"N50_B_P_L5_ci", lite:"L5", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"B", id:"L5 ce", mesh:"N50_B_P_L5_ce", lite:"L5", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"B", id:"L5 ei", mesh:"N50_B_P_L5_ei", lite:"L5", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"B", id:"L6 ci", mesh:"N50_B_P_L6_ci", lite:"L6", mm:150, face:"in", note:"centre of glass, interior", kind:"glass"},
  {bank:"B", id:"L6 ce", mesh:"N50_B_P_L6_ce", lite:"L6", mm:150, face:"out", note:"centre of glass, exterior", kind:"glass"},
  {bank:"B", id:"L6 ei", mesh:"N50_B_P_L6_ei", lite:"L6", mm:35, face:"in", note:"edge of glass, interior", kind:"glass"},
  {bank:"B", id:"air in 1", mesh:"N50_B_P_air_in1", lite:"room", mm:0, face:"in", note:"interior ambient air", kind:"air"},
  {bank:"B", id:"air out 1", mesh:"N50_B_P_air_out1", lite:"outside", mm:0, face:"out", note:"exterior ambient air", kind:"air"},
];
const noise = PROBES.map(()=>({v:0}));
function tick(dt){ noise.forEach(n=>{ n.v = n.v*0.96 + (Math.random()-0.5)*0.12; }); }
let LIVE=null;  // {time_utc, probes:{id:{value_f,...}}, weather:{...}} from bridge/poll_lab.py
async function fetchLive(){
  try{ const r=await fetch("https://raw.githubusercontent.com/feldtdesign-ship-it/n50-lab-live/lab-data/latest.json?t="+Math.floor(Date.now()/60000),{cache:"no-store"}); if(!r.ok) throw 0; const j=await r.json();
    const age=(Date.now()-new Date(j.time_utc))/60000; LIVE = age<90 ? j : null;
    const el=$("pillSim"); if(LIVE){ el.textContent="LIVE SENSORS "+j.time_utc.slice(11,16)+" UTC"; el.classList.remove("sim"); el.classList.add("live"); }
    else { el.textContent="SENSORS OFFLINE · last data "+Math.round(age/60)+" h ago"; }
    if(LIVE&&LIVE.weather&&LIVE.weather.temp_f!=null){ $("wTs").textContent="weather station on the lab roof"; if(state.live){ state.tout=LIVE.weather.temp_f; $("tout").value=Math.round(state.tout); } }
    try{ let n=0; for(const i of [1,2,3]){ const p=((LIVE&&LIVE.probes)||{})["C"+i]; if(p&&p.value_f!=null){ n++; $("c"+i).innerHTML=`<div class="s">C${i}</div><div class="v">${p.value_f.toFixed(1)}<small>F</small></div><div class="s">live</div>`; } }
      $("cState").textContent=n?n+" of 3 live":"standby · 3 sensors linked"; }catch(e){}
    update(); renderNsgl();
  }catch(e){ LIVE=null; }
}
function readings(tin,tout){
  return PROBES.map((p,i)=> ({...p, t: (p.kind==="air" ? (p.face==="out"?tout:tin) : p.face==="out" ? extSurf(tin,tout,p.mm) : surf(p.mm,tin,tout)) + noise[i].v,
                               model: p.kind==="air" ? (p.face==="out"?tout:tin) : p.face==="out" ? extSurf(tin,tout,p.mm) : surf(p.mm,tin,tout)}))
    .map(r=>{ const lv=LIVE&&LIVE.probes&&(LIVE.probes[r.bank+":"+r.id]||LIVE.probes[r.id]); return (lv&&lv.value_f!=null) ? {...r, t:lv.value_f, live:true} : r; });
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
  state.atF=(pf&&pf.t!=null)?pf.t:null;
  $("wApts").textContent= pf ? (pf.text||"")+" · observed "+pf.time.slice(11,16)+" UTC · lab "+(c.temperature_2m-at>=0?"+":"")+(c.temperature_2m-at).toFixed(1)+" F" : (a? "model cell · lab "+(c.temperature_2m-at>=0?"+":"")+(c.temperature_2m-at).toFixed(1)+" F" : "valley reference");
  renderNsgl();
}
const SLOPE_GAIN_F=11;  // historical Oct-Mar mean, slope stations 1,100-1,150 ft vs Fairbanks Intl (14-station study, 17 Aug)
function renderNsgl(){ const P=(LIVE&&LIVE.probes)||{}, o=["A:air out 1","B:air out 1"].map(k=>P[k]&&P[k].value_f).filter(v=>v!=null), at=state.atF, f=v=>v.toFixed(1);
  let est=null, s="waiting for data";
  if(o.length){ const lab=o.reduce((a,b)=>a+b,0)/o.length; est=lab; s="lab outside probes "+f(lab)+" F, real"+(at!=null?" · Fairbanks Intl "+f(at)+" F · slope "+(lab-at>=0?"+":"")+f(lab-at)+" F":"")+" · lodge is 23 ft lower, no correction"; }
  else if(at!=null){ est=at+SLOPE_GAIN_F; s="Fairbanks Intl "+f(at)+" F + historical slope gain "+SLOPE_GAIN_F+" F · lab probes offline"; }
  if(o.length){ $("wT").innerHTML=f(est)+"<small>F</small>"; $("wTs").textContent="measured at the lab, outside probes"; } else { $("wT").innerHTML="--<small>F</small>"; $("wTs").textContent="lab probes offline"; }
  const ia=["A:air in 1","B:air in 1"].map(k=>P[k]&&P[k].value_f).filter(v=>v!=null); $("wIn").innerHTML=(ia.length?f(ia.reduce((a,b)=>a+b,0)/ia.length):"--")+"<small>F</small>"; $("wIns").textContent=ia.length?"measured at the lab, inside probes":"lab probes offline";
  const pa=state.pafa; if(at==null){ $("wApt").innerHTML="--<small>F</small>"; $("wApts").textContent="no live observation"; } else { $("wApt").innerHTML=f(at)+"<small>F</small>"; $("wApts").textContent="National Weather Service"+(pa&&pa.time?" · observed "+pa.time.slice(11,16)+" UTC":"")+(o.length?" · lab "+((est-at)>=0?"+":"")+f(est-at)+" F":""); }
  $("wN").innerHTML=(est==null?"--":f(est))+"<small>F</small>"; $("wNs").textContent=s; }
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
  rs.filter(r=>r.bank===b).forEach(r=>{ const tr=document.createElement("tr");
    tr.innerHTML=`<td><span class="st" style="background:${!r.live?"#5E7490":r.face==="out"?"#9FD9E8":colorFor(r.t,state.tin,state.tout)}"></span>${r.id}<div class="delta">${r.note}</div></td><td>${r.lite}</td><td class="num">${r.kind==="air"?"air":r.face==="out"?"ext":r.mm+" mm"}</td><td class="num" style="color:var(--cream)">${r.live?r.t.toFixed(1)+" F <span class=\"delta\" style=\"color:var(--ok)\">live</span>":"<span class=\"delta\">no reading</span>"}</td>`;
    tb.appendChild(tr); }); });
}

// ---------- section trace ----------
// ---------- 3D walls, Blender model, one viewer per wall ----------
const viewers={};
const BANKS = { A:{center:[0,1.7,0], dist:7.2}, B:{center:[9,2.3,0], dist:7.6} };
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
      if(/^N50_[AB]_(glass|transom)_[0-9]/.test(k)){ const bb=new THREE.Box3().setFromObject(o); const sz=new THREE.Vector3(); bb.getSize(sz); const ctr=new THREE.Vector3(); bb.getCenter(ctr);
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
const FRAME_BELOW_EDGE_F=4;  // ASSUMED: no frame probe yet; frames drawn this far below the coldest live glass edge
function liveBank(b){ const P=LIVE&&LIVE.probes; if(!P) return null; const px=b==="A"?"V":"L", g=s=>Object.entries(P).filter(([k,p])=>k[0]===px&&k.endsWith(" "+s)&&p&&p.value_f!=null).map(([,p])=>p.value_f);
  const ci=g("ci"), ei=g("ei"), ce=g("ce"), ai=P[b+":air in 1"], ao=P[b+":air out 1"]; if(!ci.length||!ei.length||!ce.length||!ai||ai.value_f==null||!ao||ao.value_f==null) return null;
  const av=a=>a.reduce((x,y)=>x+y,0)/a.length; return {ci:av(ci), ei:av(ei), ce:av(ce), fr:Math.min(...ei)-FRAME_BELOW_EDGE_F, ain:ai.value_f, aout:ao.value_f}; }
function thermalRange(){ const lo=Math.min(state.tout, surf(0,state.tin,state.tout))-3, hi=state.tin+2; return [lo,hi]; }
function applyThermal(){
  ["A","B"].forEach(b=>{ const v=viewers[b]; if(!v||!v.scene) return;
    const LB=liveBank(b); if(!LB){ $("tscale"+b).hidden=true; v.glass.forEach(m=>{ m.visible=false; }); v.scene.traverse(o=>{ if(o.isMesh&&v.orig.has(o)) o.material=v.orig.get(o); }); return; }
    const [lo,hi]=LB?[LB.fr-2,LB.ci+10]:thermalRange(); const n=u=>(u-lo)/(hi-lo);
    $("tscale"+b).querySelector("em").textContent=LB?"LIVE GLASS · FRAME + WALL ESTIMATED":"NO LIVE DATA";
    $("tscale"+b).hidden=false; $("tscale"+b).querySelector(".mx").textContent=hi.toFixed(1); $("tscale"+b).querySelector(".mn").textContent=lo.toFixed(1);
    v.scene.traverse(o=>{ if(!o.isMesh) return; const k=(o.name||(o.parent&&o.parent.name)||"").replace(/\.\d+$/,"");
      if(!state.thermal){ if(v.orig.has(o)) o.material=v.orig.get(o); return; }
      if(/_P_/.test(k)) return;
      // walls and frames: grade from the outdoor face to the room face through the thickness, so reveals show the gradient
      const isFrame=/_(mull|head|sill|transom_bar|jamb)/.test(k);
      const tIn = LB ? (isFrame ? LB.fr : LB.ain-8) : (isFrame ? surf(6,state.tin,state.tout)-1.5 : state.tin-1.2);
      const tOut = LB ? LB.aout + (isFrame?0.06:0.03)*(LB.ain-LB.aout) : state.tout + (isFrame?0.06:0.03)*(state.tin-state.tout);
      const g=o.geometry; if(!g.attributes.color){ g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(g.attributes.position.count*3),3)); }
      g.computeBoundingBox(); const bb=g.boundingBox; const pos=g.attributes.position, col=g.attributes.color;
      // local z runs outdoor (min) to room (max) for every box in this model
      for(let i=0;i<pos.count;i++){ const u=(pos.getZ(i)-bb.min.z)/((bb.max.z-bb.min.z)||1); const t=tOut+(tIn-tOut)*u; const c=iron(n(t)); col.setXYZ(i,c[0],c[1],c[2]); }
      col.needsUpdate=true;
      if(!o.userData.tm) o.userData.tm=new THREE.MeshBasicMaterial({vertexColors:true}); o.material=o.userData.tm; });
    v.glass.forEach(m=>{ m.visible=true; const pos=m.geometry.attributes.position, col=m.geometry.attributes.color, w=m.userData.w, h=m.userData.h;
      for(let i=0;i<pos.count;i++){ const x=pos.getX(i), y=pos.getY(i); const mm=Math.max(0,Math.min(w/2-Math.abs(x), h/2-Math.abs(y))*1000); const t=LB ? (m.userData.face==="out" ? LB.ce+(extSurf(70,0,mm)-extSurf(70,0,150))*(LB.ain-LB.aout)/70 : LB.ei+(surf(mm,70,0)-surf(6,70,0))/(surf(150,70,0)-surf(6,70,0))*(LB.ci-LB.ei)) : (m.userData.face==="out" ? extSurf(state.tin,state.tout,mm) : surf(mm,state.tin,state.tout)); const c=iron(n(t)); col.setXYZ(i,c[0],c[1],c[2]); } col.needsUpdate=true; });
  });
}
function setView(th){ state.thermal=th; $("vModel").classList.toggle("on",!th); $("vTherm").classList.toggle("on",th); update(); }
function paintProbes(rs){ rs.forEach(r=>{ const v=viewers[r.bank]; if(!v||!v.pm) return; const m=v.pm[r.mesh]; if(!m) return; if(!r.live){ m.material.color.set(0x5E7490); m.material.emissive.set(0x000000); return; } if(r.face==="out"){ m.material.color.set(0x9fd9e8); m.material.emissive.set(0x0f3040); return; } const c=new THREE.Color(colorFor(r.t,state.tin,state.tout)); m.material.color.copy(c); m.material.emissive.copy(c).multiplyScalar(.3); }); }
// ---------- loop ----------
function update(){ tick(); const rs=readings(state.tin,state.tout); renderTable(rs); paintProbes(rs); applyThermal(); }
$("tin").addEventListener("input",e=>{ state.tin=+e.target.value; $("tinv").textContent=state.tin+" F"; update(); });
$("tout").addEventListener("input",e=>{ state.tout=+e.target.value; state.live=false; $("toutv").textContent=state.tout+" F"; $("liveBtn").classList.remove("on"); update(); });
$("liveBtn").addEventListener("click",()=>{ state.live=true; $("liveBtn").classList.add("on");
$("vModel").addEventListener("click",()=>setView(false)); $("vTherm").addEventListener("click",()=>setView(true)); if(state.wx){ state.tout=state.wx.temperature_2m; $("tout").value=Math.round(state.tout); } $("toutv").textContent="live"; update(); });
$("liveBtn").classList.add("on");
$("vModel").addEventListener("click",()=>setView(false)); $("vTherm").addEventListener("click",()=>setView(true));
function clock(){ const d=new Date(); $("clock").textContent=d.toLocaleTimeString("en-US",{timeZone:"America/Anchorage",hour12:false})+" AK"; }
setInterval(clock,1000); clock();
initThree(); update(); setInterval(update,2000);
fetchWx(); setInterval(fetchWx,600000);
fetchLive(); setInterval(fetchLive,300000);
</script>
"""
HTML = HTML.replace("__SAMPLE__", open(f"{S}/wx_sample_min.json").read()).replace("__MARK__", MARK).replace("__CAMH__", CAM_H).replace("__CAML__", CAM_L).replace("__GLB__", GLB).replace("__IR1__", IR1).replace("__IR2__", IR2)
out = f"{S}/n50_lab_live.html"; open(out, "w").write(HTML); print("wrote", out, len(HTML)//1024, "KB")
local = "/Users/michaelweinfeld/Documents/2026/N50/reports/Field Report 01 - Window Sensors/N50_Lab_Live_local.html"
open(local, "w").write("<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body>" + HTML + "</body></html>"); print("local copy written")
