# Blender (Cycles) urun render'i.
# Kullanim:
#   blender -b -P render.py -- <stl_klasoru> <sahne: hero|side|exploded|phone> <cikti.png> [ornek_sayisi]
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, SCENE, OUT = argv[0], argv[1], argv[2]
SAMPLES = int(argv[3]) if len(argv) > 3 else 128
PERCENT = int(argv[4]) if len(argv) > 4 else 100
MM = 0.001

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------------------------------------------------------- render
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = False
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.006
try:
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
sc.cycles.max_bounces = 8
sc.cycles.glossy_bounces = 4
sc.cycles.sample_clamp_indirect = 2.0
sc.cycles.blur_glossy = 1.0
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.render.film_transparent = False
sc.view_settings.view_transform = 'AgX' if 'AgX' in [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
try:
    sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass
sc.render.image_settings.file_format = 'PNG'

# ---------------------------------------------------------------- malzemeler
def principled(name, color, metallic=0.0, rough=0.4, coat=0.0, bevel=0.35, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    for key in ("Coat Weight", "Clearcoat"):
        if key in b.inputs:
            b.inputs[key].default_value = coat
            break
    for key in ("Specular IOR Level", "Specular"):
        if key in b.inputs:
            b.inputs[key].default_value = spec
            break
    if bevel > 0:  # keskin kenarlarda yumusak isik yansimasi
        bv = nt.nodes.new("ShaderNodeBevel")
        bv.inputs["Radius"].default_value = bevel * MM
        bv.samples = 8
        nt.links.new(bv.outputs["Normal"], b.inputs["Normal"])
    return m

MAT = {
    "silver": principled("silver", (0.50, 0.51, 0.53), metallic=0.85, rough=0.27),
    "black":  principled("black", (0.012, 0.012, 0.014), rough=0.36, coat=0.15),
    "steel":  principled("steel", (0.78, 0.78, 0.80), metallic=1.0, rough=0.20, bevel=0.15),
    "pad":    principled("pad", (0.85, 0.22, 0.04), rough=0.65, bevel=0.2),
}
PART_MAT = {"frame": "silver", "knob": "silver", "plunger": "silver",
            "jaw": "black", "cap": "black", "screw": "steel", "nut": "steel",
            "pad1": "pad", "pad2": "pad"}

def import_stl(path):
    before = set(bpy.data.objects)
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=path)
    else:
        bpy.ops.import_mesh.stl(filepath=path)
    return [o for o in bpy.data.objects if o not in before][0]

def load_clamp(coll):
    for name, mat in PART_MAT.items():
        p = os.path.join(SRC, name + ".stl")
        if not os.path.exists(p):
            continue
        o = import_stl(p)
        o.name = name
        o.scale = (MM, MM, MM)
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
        me = o.data
        me.materials.clear()
        me.materials.append(MAT[mat])
        # auto smooth: silindirler puruzsuz, keskin kenarlar keskin
        bpy.context.view_layer.objects.active = o
        for poly in me.polygons:
            poly.use_smooth = True
        if hasattr(me, "use_auto_smooth"):
            me.use_auto_smooth = True
            me.auto_smooth_angle = math.radians(32)
        else:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(32))

# ---------------------------------------------------------------- isik / stüdyo
def studio(cam_loc, floor_col=(0.80, 0.81, 0.83)):
    cx, cy = cam_loc[0], cam_loc[1]
    n = math.hypot(cx, cy)
    fx, fy = cx / n, cy / n          # hedeften kameraya (yatay)
    rx, ry = fy, -fx                 # kameradan bakinca sag
    def L(u, v, z):                  # u: kameraya dogru, v: saga
        return (u * fx + v * rx, u * fy + v * ry, z)
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*floor_col, 1)
    bg.inputs["Strength"].default_value = 0.25

    # sonsuz fon (yukari kivrilan zemin)
    bpy.ops.mesh.primitive_plane_add(size=1)
    fl = bpy.context.object
    fl.scale = (3, 3, 1)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=40)
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in fl.data.vertices:   # arkada yumusak kivrim
        y = v.co.y * 3
        if y > 0.08:
            v.co.z = ((y - 0.08) ** 2) * 4
    fl.rotation_euler[2] = math.atan2(cx, -cy)
    for p in fl.data.polygons:
        p.use_smooth = True
    fm = principled("floor", floor_col, rough=0.55, bevel=0)
    fl.data.materials.append(fm)

    def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.03)):
        bpy.ops.object.light_add(type='AREA', location=loc)
        l = bpy.context.object
        l.name = name
        l.data.shape = 'RECTANGLE'
        l.data.size, l.data.size_y = size
        l.data.energy = energy
        l.data.color = color
        d = Vector(target) - l.location
        l.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return l
    area("key",  L(0.20, -0.30, 0.35), (0.30, 0.30), 5.5, (1.0, 0.97, 0.93))
    area("fill", L(0.30, 0.28, 0.14), (0.35, 0.25), 2.2, (0.92, 0.96, 1.0))
    area("rim",  L(-0.30, 0.15, 0.22), (0.25, 0.10), 6)
    area("top",  (0.0, 0.0, 0.55), (0.40, 0.40), 2)

def camera(loc, target, lens=85, fstop=None, focus=None):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    cam.data.sensor_width = 36
    if fstop:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_distance = focus if focus else d.length
    sc.camera = cam
    return cam

# ---------------------------------------------------------------- telefon modeli
def phone(center_z):
    L, Wd, T = 0.150, 0.072, 0.0080
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, center_z))
    body = bpy.context.object
    body.scale = (L, Wd, T)
    bpy.ops.object.transform_apply(scale=True)
    bv = body.modifiers.new("b", 'BEVEL')
    bv.width = 0.0035
    bv.segments = 10
    body.data.materials.append(principled("phone_frame", (0.16, 0.17, 0.19), metallic=0.9, rough=0.25, bevel=0))
    bpy.ops.object.shade_smooth()

    # ekran camı + duvar kagidi
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, center_z + T/2 + 0.00005))
    scr = bpy.context.object
    scr.scale = (L - 0.0045, Wd - 0.0045, 1)
    m = bpy.data.materials.new("screen")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    b.inputs["Roughness"].default_value = 0.03
    tc = nt.nodes.new("ShaderNodeTexCoord")
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = 'LINEAR'
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value[2] = math.radians(25)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.02, 0.05, 0.25, 1)
    ramp.color_ramp.elements[1].color = (0.55, 0.12, 0.45, 1)
    e = ramp.color_ramp.elements.new(0.5)
    e.color = (0.05, 0.25, 0.55, 1)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    key = "Emission Color" if "Emission Color" in b.inputs else "Emission"
    nt.links.new(ramp.outputs["Color"], b.inputs[key])
    if "Emission Strength" in b.inputs:
        b.inputs["Emission Strength"].default_value = 1.2
    scr.data.materials.append(m)

# ---------------------------------------------------------------- sahneler
clamp = bpy.data.collections.new("clamp")
sc.collection.children.link(clamp)
load_clamp(clamp)

if SCENE in ("hero", "side", "exploded"):
    # parcalar dogrudan sahnede
    if SCENE == "hero":
        sc.render.resolution_x, sc.render.resolution_y = 1200, 1560
        camera((0.215, 0.150, 0.115), (0.0, 0.010, 0.032), lens=90, fstop=16)
    elif SCENE == "side":
        sc.render.resolution_x, sc.render.resolution_y = 1200, 1560
        camera((0.300, 0.050, 0.075), (0.0, 0.010, 0.032), lens=100, fstop=16)
    else:
        sc.render.resolution_x, sc.render.resolution_y = 1200, 1700
        camera((0.330, 0.220, 0.200), (0.012, 0.010, 0.066), lens=82)
else:  # phone: 4 klips telefonu tutuyor
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1260
    sc.collection.children.unlink(clamp)
    z_ph = (5.0 + 0.4 + 4.0) * MM  # alt ped ustu + yarim kalinlik
    phone(z_ph)
    for x in (-0.045, 0.045):
        for side in (1, -1):
            e = bpy.data.objects.new("c", None)
            e.instance_type = 'COLLECTION'
            e.instance_collection = clamp
            e.rotation_euler = (0, 0, 0 if side < 0 else math.pi)
            e.location = (x, side * (0.036 + 0.005), 0)
            sc.collection.objects.link(e)
    camera((0.250, -0.360, 0.300), (0.0, 0.0, 0.012), lens=70, fstop=22)

studio(sc.camera.location)
sc.render.resolution_percentage = PERCENT
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
