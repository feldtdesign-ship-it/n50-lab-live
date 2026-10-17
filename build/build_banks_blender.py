# N50 lab window banks, Blender 5. Standalone: run headless with
#   /Applications/Blender.app/Contents/MacOS/Blender --background --python build_banks_blender.py -- /path/out.glb
# Metres.
# Bank A, V Wall: three openings in drywall, 36 x 80 in assumed. V1 to V3 left to right.
# Bank B, L Wall: one frame, three lites across and two high. Lower 44 x 86 in, upper 44 x 48 in,
#   scaled off the 36 x 80 in door. Numbered right to left from inside: top row L3 L2 L1, bottom row L6 L5 L4 (confirmed 17 Oct).
# Probes per lite: centre of glass interior, centre of glass exterior, edge of glass interior.
#   One interior and one exterior ambient air thermocouple per wall.
import bpy, sys, os
from mathutils import Vector
IN = 0.0254

def clear():
    for o in list(bpy.data.objects):
        if o.name.startswith("N50_"): bpy.data.objects.remove(o, do_unlink=True)

def mat(name, rgba, rough=0.6, metal=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = rgba; b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal; b.inputs["Alpha"].default_value = alpha
    try:
        if alpha < 1: m.blend_method = "BLEND"
    except Exception: pass
    return m

M_FRAME = mat("N50_frame_white", (0.91, 0.90, 0.87, 1), 0.5)
M_GLASS = mat("N50_glass", (0.55, 0.72, 0.80, 1), 0.05, 0, 0.25)
M_CLAD  = mat("N50_cladding", (0.16, 0.13, 0.11, 1), 0.9)
M_WALL  = mat("N50_drywall", (0.80, 0.78, 0.74, 1), 0.95)
M_PROBE = mat("N50_probe", (0.92, 0.71, 0.25, 1), 0.4)
M_PROBE_X = mat("N50_probe_ext", (0.62, 0.85, 0.91, 1), 0.4)
M_WIRE  = mat("N50_wire", (0.25, 0.25, 0.25, 1), 0.8)
M_PLY   = mat("N50_ply", (0.62, 0.45, 0.25, 1), 0.8)

def box(name, size, loc, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object
    o.name = name; o.scale = Vector(size); o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def empty(name, loc):
    o = bpy.data.objects.new(name, None); o.location = loc; bpy.context.scene.collection.objects.link(o); return o

def probe(name, loc, parent, ext=False, lead_to_z=None, r=0.02):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=16, ring_count=10)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(M_PROBE_X if ext else M_PROBE); o.parent = parent
    if lead_to_z is not None:
        cu = bpy.data.curves.new(name + "_wire", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0015
        sp = cu.splines.new("POLY"); sp.points.add(1)
        sp.points[0].co = (loc[0], loc[1], loc[2], 1); sp.points[1].co = (loc[0] + 0.03, loc[1], lead_to_z, 1)
        w = bpy.data.objects.new(name + "_wire", cu); w.data.materials.append(M_WIRE); bpy.context.scene.collection.objects.link(w); w.parent = parent
    return o

def wall_around(prefix, m, parent, x0, x1, z0, z1, ox0, ox1, oz0, oz1, depth=0.30):
    box(prefix + "_L", (ox0 - x0, depth, z1 - z0), ((x0 + ox0) / 2, 0, (z0 + z1) / 2), m, parent)
    box(prefix + "_R", (x1 - ox1, depth, z1 - z0), ((ox1 + x1) / 2, 0, (z0 + z1) / 2), m, parent)
    box(prefix + "_T", (ox1 - ox0, depth, z1 - oz1), ((ox0 + ox1) / 2, 0, (oz1 + z1) / 2), m, parent)
    box(prefix + "_B", (ox1 - ox0, depth, oz0 - z0), ((ox0 + ox1) / 2, 0, (z0 + oz0) / 2), m, parent)

clear()
fw, D = 0.07, 0.30
yI, yX = -0.015, 0.015
e = 0.035   # edge probe, 35 mm in from the sight line

# ---------- Bank A, V Wall (three openings) ----------
A = empty("N50_BankA_VWall", (0, 0, 0))
ow, oh, osill = 36 * IN, 80 * IN, 0.70; ops = [-2.0, 0.0, 2.0]
piers = [(-3.3, ops[0] - ow / 2 - fw), (ops[0] + ow / 2 + fw, ops[1] - ow / 2 - fw), (ops[1] + ow / 2 + fw, ops[2] - ow / 2 - fw), (ops[2] + ow / 2 + fw, 3.3)]
for i, (a, b) in enumerate(piers): box(f"N50_A_pier_{i}", (b - a, D, oh + 2 * fw), ((a + b) / 2, 0, osill + oh / 2), M_WALL, A)
box("N50_A_wall_T", (6.6, D, 3.2 - (osill + oh + fw)), (0, 0, (osill + oh + fw + 3.2) / 2), M_WALL, A)
box("N50_A_wall_B", (6.6, D, osill - fw), (0, 0, (osill - fw) / 2), M_WALL, A)
for i, x in enumerate(ops):
    box(f"N50_A_glass_{i+1}", (ow, 0.02, oh), (x, 0.0, osill + oh / 2), M_GLASS, A)
    box(f"N50_A_jambL_{i+1}", (fw, D, oh + 2 * fw), (x - ow / 2 - fw / 2, 0.0, osill + oh / 2), M_FRAME, A)
    box(f"N50_A_jambR_{i+1}", (fw, D, oh + 2 * fw), (x + ow / 2 + fw / 2, 0.0, osill + oh / 2), M_FRAME, A)
    box(f"N50_A_head_{i+1}", (ow + 2 * fw, D, fw), (x, 0.0, osill + oh + fw / 2), M_FRAME, A)
    box(f"N50_A_sill_{i+1}", (ow + 2 * fw, D, fw), (x, 0.0, osill - fw / 2), M_FRAME, A)
box("N50_A_plywood", (0.55, 0.02, 0.70), (1.05, -D / 2 - 0.01, 1.70), M_PLY, A)
for i, x in enumerate(ops):
    z = osill + oh * 0.5
    probe(f"N50_A_P_V{i+1}_ci", (x, yI, z), A, lead_to_z=osill + oh)
    probe(f"N50_A_P_V{i+1}_ce", (x, yX, z), A, ext=True, lead_to_z=osill + oh)
    probe(f"N50_A_P_V{i+1}_ei", (x - ow / 2 + e, yI, z), A, lead_to_z=osill + oh)
probe("N50_A_P_air_in1", (-1.0, -0.45, osill + oh - 0.2), A, lead_to_z=osill + oh + 0.3, r=0.025)
probe("N50_A_P_air_out1", (-1.0, 0.45, osill + oh - 0.2), A, ext=True, lead_to_z=osill + oh + 0.3, r=0.025)

# ---------- Bank B, L Wall (one frame, six lites) ----------
B = empty("N50_BankB_LWall", (9.0, 0.0, 0.0))
uw, uh, th = 44 * IN, 86 * IN, 48 * IN; sill = 0.50
cols = [-(uw + fw), 0.0, (uw + fw)]
z_low = sill + uh / 2; z_hi = sill + uh + fw + th / 2; head = sill + uh + fw + th
ox0, ox1 = -(1.5 * uw + 2 * fw), (1.5 * uw + 2 * fw); oz0, oz1 = sill - fw, head + fw
wall_around("N50_B_wall", M_CLAD, B, ox0 - 1.0, ox1 + 1.0, 0.0, oz1 + 0.5, ox0, ox1, oz0, oz1, D)
for i, x in enumerate(cols):
    box(f"N50_B_glass_{6-i}", (uw, 0.02, uh), (x, 0.0, z_low), M_GLASS, B)   # bottom row, large: L6 L5 L4
    box(f"N50_B_glass_{3-i}", (uw, 0.02, th), (x, 0.0, z_hi), M_GLASS, B)    # top row, small: L3 L2 L1
for i, x in enumerate([-1.5 * uw - 1.5 * fw, -0.5 * uw - 0.5 * fw, 0.5 * uw + 0.5 * fw, 1.5 * uw + 1.5 * fw]):
    box(f"N50_B_mull_{i}", (fw, D, head - sill + 2 * fw), (x, 0.0, (sill + head) / 2), M_FRAME, B)
box("N50_B_transom_bar", (3 * uw + 4 * fw, D, fw), (0, 0.0, sill + uh + fw / 2), M_FRAME, B)
box("N50_B_head", (3 * uw + 4 * fw, D, fw), (0, 0.0, head + fw / 2), M_FRAME, B)
box("N50_B_sill", (3 * uw + 4 * fw, D, fw), (0, 0.0, sill - fw / 2), M_FRAME, B)
# Numbered right to left as seen from inside: top L3 L2 L1, bottom L6 L5 L4 (Michael, 17 Oct).
for row, (zc, top, n0) in enumerate([(sill + uh * 0.5, sill + uh, 6), (z_hi, head, 3)]):
    for i, x in enumerate(cols):
        n = n0 - i
        probe(f"N50_B_P_L{n}_ci", (x, yI, zc), B, lead_to_z=top)
        probe(f"N50_B_P_L{n}_ce", (x, yX, zc), B, ext=True, lead_to_z=top)
        xe = x + uw / 2 - e if i < 2 else x - uw / 2 + e
        probe(f"N50_B_P_L{n}_ei", (xe, yI, zc), B, lead_to_z=top)
probe("N50_B_P_air_in1", (-0.9, -0.45, head - 0.3), B, lead_to_z=head + 0.2, r=0.025)
probe("N50_B_P_air_out1", (-0.9, 0.45, head - 0.3), B, ext=True, lead_to_z=head + 0.2, r=0.025)

# ---------- export ----------
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "N50_window_banks.glb")
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.name.startswith("N50_"): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True, export_yup=True, export_materials='EXPORT')
print("built", len([o for o in bpy.data.objects if "_P_" in o.name and not o.name.endswith("_wire")]), "probes ->", out)
