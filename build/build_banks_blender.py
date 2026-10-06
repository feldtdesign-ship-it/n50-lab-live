# N50 lab window banks. Runs inside Blender via MCP. Metres.
# Bank A from the UniFi "Vitro Wall" camera frame, scaled off a 36 x 80 in door. Lower row = three 44 x 86 in Vitro VIG units (NFBS memo, 1 June 2026).
# Bank B from the "LuxWall" camera frame. Opening size assumed, flagged.
import bpy
from mathutils import Vector
IN = 0.0254

def clear():
    for o in list(bpy.data.objects):
        if o.name.startswith("N50_"): bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.curves):
        if c.name.startswith("N50_") and c.users == 0: bpy.data.curves.remove(c)

def mat(name, rgba, rough=0.6, metal=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Alpha"].default_value = alpha
    try:
        if alpha < 1: m.blend_method = "BLEND"
    except Exception: pass
    return m

M_FRAME = mat("N50_frame_white", (0.91, 0.90, 0.87, 1), 0.5)
M_GLASS = mat("N50_glass", (0.55, 0.72, 0.80, 1), 0.05, 0, 0.25)
M_CLAD  = mat("N50_cladding", (0.16, 0.13, 0.11, 1), 0.9)
M_WALL  = mat("N50_drywall", (0.80, 0.78, 0.74, 1), 0.95)
M_DOOR  = mat("N50_door", (0.20, 0.22, 0.24, 1), 0.6)
M_PROBE = mat("N50_probe", (0.92, 0.71, 0.25, 1), 0.4)
M_PROBE_X = mat("N50_probe_ext", (0.62, 0.85, 0.91, 1), 0.4)
M_WIRE  = mat("N50_wire", (0.25, 0.25, 0.25, 1), 0.8)
M_PLY   = mat("N50_ply", (0.62, 0.45, 0.25, 1), 0.8)

def box(name, size, loc, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = Vector(size)
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def empty(name, loc):
    o = bpy.data.objects.new(name, None); o.location = loc; bpy.context.scene.collection.objects.link(o); return o

def probe(name, loc, parent, ext=False, lead_to_z=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=loc, segments=16, ring_count=10)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(M_PROBE_X if ext else M_PROBE); o.parent = parent
    if lead_to_z is not None:
        cu = bpy.data.curves.new(name+"_wire", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0015
        sp = cu.splines.new("POLY"); sp.points.add(1)
        sp.points[0].co = (loc[0], loc[1], loc[2], 1); sp.points[1].co = (loc[0]+0.03, loc[1], lead_to_z, 1)
        w = bpy.data.objects.new(name+"_wire", cu); w.data.materials.append(M_WIRE); bpy.context.scene.collection.objects.link(w); w.parent = parent
    return o

clear()
fw = 0.07          # frame member face width
yI, yX = -0.015, 0.015   # interior face, exterior face

# ---------- Bank A: house "Vitro Wall". 3 columns x 2 rows. Lower row 44 x 86 in Vitro units, upper row 44 x 48 in transoms. ----------
A = empty("N50_BankA_VitroWall", (0, 0, 0))
uw, uh, th = 44*IN, 86*IN, 48*IN          # unit width, unit height, transom height
sill = 0.50
cols = [-(uw+fw), 0.0, (uw+fw)]           # x centres
z_low = sill + uh/2; z_hi = sill + uh + fw + th/2; head = sill + uh + fw + th
wall_w = 3*uw + 4*fw + 1.6
box("N50_A_wall", (wall_w, 0.30, head + 0.6), (0.2, 0.18, (head+0.6)/2), M_CLAD, A)
for i, x in enumerate(cols):
    box(f"N50_A_vitro_{i+1}", (uw, 0.02, uh), (x, 0.0, z_low), M_GLASS, A)
    box(f"N50_A_transom_{i+1}", (uw, 0.02, th), (x, 0.0, z_hi), M_GLASS, A)
# mullions, transom bar, head, sill
for i, x in enumerate([-1.5*uw-1.5*fw, -0.5*uw-0.5*fw, 0.5*uw+0.5*fw, 1.5*uw+1.5*fw]):
    box(f"N50_A_mull_{i}", (fw, 0.12, head - sill + 2*fw), (x, 0.0, (sill+head)/2), M_FRAME, A)
box("N50_A_transom_bar", (3*uw+4*fw, 0.12, fw), (0, 0.0, sill + uh + fw/2), M_FRAME, A)
box("N50_A_head", (3*uw+4*fw, 0.12, fw), (0, 0.0, head + fw/2), M_FRAME, A)
box("N50_A_sill", (3*uw+4*fw, 0.14, fw), (0, 0.0, sill - fw/2), M_FRAME, A)
# the door, left of the wall, for scale: 36 x 80 in
dx = -(1.5*uw + 2*fw) - 0.35 - 18*IN
box("N50_A_door", (36*IN, 0.05, 80*IN), (dx, -0.02, 40*IN), M_DOOR, A)
box("N50_A_door_lite", (24*IN, 0.06, 60*IN), (dx, -0.02, 48*IN), M_GLASS, A)
# probes: each Vitro unit carries an inside and an outside probe at the same station, plus the sight line pair on unit 2.
for i, x in enumerate(cols):
    z = sill + uh*0.72
    probe(f"N50_A_P_unit{i+1}_in",  (x, yI, z), A, lead_to_z=sill+uh)
    probe(f"N50_A_P_unit{i+1}_out", (x, yX, z), A, ext=True, lead_to_z=sill+uh)
xe = cols[1] - uw/2 + 0.035
probe("N50_A_P_edge_in_sightline", (xe, yI, sill + uh*0.55), A, lead_to_z=sill+uh)
probe("N50_A_P_edge_out_seal",     (xe, yX, sill + uh*0.55), A, ext=True)

# ---------- Bank B: lab "LuxWall". Three punched openings in drywall, plywood panel between 2 and 3. Opening size assumed 36 x 80 in. ----------
B = empty("N50_BankB_LuxWall", (0, 5.0, 0))
ow, oh, osill = 36*IN, 80*IN, 0.70
ops = [-2.0, 0.0, 2.0]
box("N50_B_wall", (6.6, 0.30, 3.2), (0, 0.18, 1.6), M_WALL, B)
for i, x in enumerate(ops):
    box(f"N50_B_glass_{i+1}", (ow, 0.02, oh), (x, 0.0, osill + oh/2), M_GLASS, B)
    box(f"N50_B_jambL_{i+1}", (fw, 0.12, oh + 2*fw), (x - ow/2 - fw/2, 0.0, osill + oh/2), M_FRAME, B)
    box(f"N50_B_jambR_{i+1}", (fw, 0.12, oh + 2*fw), (x + ow/2 + fw/2, 0.0, osill + oh/2), M_FRAME, B)
    box(f"N50_B_head_{i+1}", (ow + 2*fw, 0.12, fw), (x, 0.0, osill + oh + fw/2), M_FRAME, B)
    box(f"N50_B_sill_{i+1}", (ow + 2*fw, 0.14, fw), (x, 0.0, osill - fw/2), M_FRAME, B)
box("N50_B_plywood", (0.55, 0.02, 0.70), (1.05, -0.02, 1.70), M_PLY, B)
for i, x in enumerate(ops):
    z = osill + oh*0.6
    probe(f"N50_B_P_op{i+1}_in",  (x, yI, z), B, lead_to_z=osill+oh)
    probe(f"N50_B_P_op{i+1}_out", (x, yX, z), B, ext=True, lead_to_z=osill+oh)
probe("N50_B_P_edge_in_sightline", (0.0 - ow/2 + 0.035, yI, osill + oh*0.5), B, lead_to_z=osill+oh)
probe("N50_B_P_edge_out_seal",     (0.0 - ow/2 + 0.035, yX, osill + oh*0.5), B, ext=True)

n = len([o for o in bpy.data.objects if o.name.startswith('N50_')])
print("built", n, "objects. Bank A head at", round(head,3), "m; unit", round(uw,3), "x", round(uh,3), "m")

# ---------- Cut back, 6 Oct 2026: only what the 2 October photographs show ----------
# Two per lite, inside and outside, on all six Vitro lites and the three LuxWall openings. Transom probes wait for Kevin's schedule.
for o in list(bpy.data.objects):
    if "_P_" in o.name and not any(k in o.name for k in ("unit1","unit2","unit3","transom","_op1","_op2","_op3")): bpy.data.objects.remove(o, do_unlink=True)
