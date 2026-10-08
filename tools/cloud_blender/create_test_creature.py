"""Cloud Blender test: a stylized four-eyed amphibious fantasy runner.
Run with: blender --background --python tools/cloud_blender/create_test_creature.py
Creates outputs/*.glb, *.blend, *.png, and *.json.
This is an experimental low-poly prototype, not an approved Worldvein model.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)

def material(name, color, glow=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = 0.72
    if glow:
        p.inputs["Emission Color"].default_value = (*color, 1.0)
        p.inputs["Emission Strength"].default_value = glow
    return m

fur = material("Warm slate fur", (0.29, 0.36, 0.42))
fur_light = material("Cream undercoat", (0.78, 0.73, 0.60))
stripe = material("Back markings", (0.12, 0.19, 0.26))
inner_ear = material("Ear interiors", (0.74, 0.42, 0.39))
eyes = material("Golden bioluminescent eyes", (0.97, 0.66, 0.12), 0.4)
dark = material("Plus sign pupils", (0.04, 0.06, 0.08))
fin = material("Gill and webbing membrane", (0.20, 0.60, 0.62))
glow = material("Amber tail light", (1.0, 0.56, 0.12), 1.2)
floor_mat = material("Preview backdrop only", (0.23, 0.27, 0.32))

asset_objects = []

def ellipsoid(name, location, scale, mat, rotation=(0,0,0), asset=True):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if asset:
        asset_objects.append(obj)
    return obj

def capsule(name, p1, p2, r, mat, asset=True):
    vec = Vector(p2) - Vector(p1)
    mid = (Vector(p1) + Vector(p2)) / 2
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=vec.length, location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = vec.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if asset:
        asset_objects.append(obj)
    return obj

def cube(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    asset_objects.append(obj)
    return obj

# Center of mass and torso; model faces negative X. Dimensions are in meters.
ellipsoid("Torso", (0.03,0,0.65), (.66,.31,.32), fur)
ellipsoid("Chest", (-.40,0,.68), (.28,.34,.34), fur)
ellipsoid("Underbelly", (-.06,0,.47), (.53,.29,.17), fur_light)
ellipsoid("Neck", (-.55,0,.72), (.24,.24,.24), fur)
ellipsoid("Head", (-.73,0,.86), (.31,.27,.27), fur)
ellipsoid("Muzzle", (-.97,0,.75), (.22,.19,.13), fur_light)
ellipsoid("Nose", (-1.17,0,.79), (.065,.085,.046), inner_ear)

# Exactly four external eyes: an upper and lower eye on each side.
# Cross-shaped pupils distinguish the species even in simple game LODs.
for side in (-1, 1):
    for row, z in enumerate((.83, 1.00)):
        eye_x = -.915 if row == 0 else -.855
        y = side * (.147 if row == 0 else .167)
        ellipsoid(f"Eye_{'L' if side<0 else 'R'}_{row+1}",
                  (eye_x,y,z), (.075,.086,.070), eyes)
        cube(f"Pupil_horizontal_{side}_{row}", (eye_x-.071,y,z),
             (.012,.070,.014), dark)
        cube(f"Pupil_vertical_{side}_{row}", (eye_x-.074,y,z),
             (.013,.015,.070), dark)

# Upright ears, neck gills, and matching back stripes.
for side in (-1,1):
    y = side * .19
    ellipsoid(f"Ear_{side}",(-.70,y,1.105),(.105,.075,.18),fur,rotation=(0,.10*side,0))
    ellipsoid(f"Ear_inner_{side}",(-.785,y,1.11),(.023,.048,.117),inner_ear)
    for i in range(3):
        ellipsoid(f"Neck_gill_{side}_{i}",
                  (-.52+i*.075, side*(.257+i*.008), .65+i*.06),
                  (.065,.025,.120),fin,rotation=(0,.25,side*.28))
for i,x in enumerate((-.29,-.05,.19,.43)):
    ellipsoid(f"Dorsal_mark_{i}",(x,0,.954-i*.018),(.07,.20,.016),stripe)

# Four distinct jointed legs with webbed digits.
for leg_x, leg_name in ((-.37,"Front"),(.47,"Rear")):
    for side in (-1,1):
        s_name = "L" if side < 0 else "R"
        y = side*.255
        ellipsoid(f"{leg_name}_{s_name}_upper",(leg_x,y,.39),(.125,.127,.235),fur)
        capsule(f"{leg_name}_{s_name}_shin",
                (leg_x,y,.37),(leg_x-.065,y+side*.018,.13),.081,fur)
        ellipsoid(f"{leg_name}_{s_name}_paw",(leg_x-.115,y,.105),(.19,.136,.086),fur)
        for k in (-1,0,1):
            digit_y = y+k*.070
            ellipsoid(f"{leg_name}_{s_name}_digit_{k}",
                      (leg_x-.255,digit_y,.075),(.102,.038,.042),fur_light)
        # Flat translucent-looking strip represents webbing between digits.
        ellipsoid(f"{leg_name}_{s_name}_web",
                  (leg_x-.208,y,.068),(.075,.102,.013),fin)

# Broad steering tail with a rudder fin and glowing tip.
capsule("Tail_base",(.61,0,.67),(.94,0,.69),.132,fur)
capsule("Tail_middle",(.92,0,.69),(1.30,0,.77),.088,fur)
ellipsoid("Tail_rudder",(1.30,0,.77),(.25,.17,.12),fin,rotation=(0,.23,0))
ellipsoid("Tail_tip",(1.49,0,.81),(.09,.09,.085),glow)

# Set object origins and apply transforms for portable glTF export.
bpy.ops.object.select_all(action="DESELECT")
for obj in asset_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = asset_objects[0]
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT/"runner_prototype.glb"), export_format="GLB",
    use_selection=True, export_apply=True, export_cameras=False,
    export_lights=False
)

# A studio floor and camera appear in the .blend preview but NOT in the GLB.
bpy.ops.object.select_all(action="DESELECT")
ellipsoid("Preview_floor",(0,0,-.09),(3.4,3.4,.085),floor_mat,asset=False)
bpy.ops.object.camera_add(location=(-3.3,-3.9,2.20))
cam = bpy.context.object
target = Vector((.10,0,.58))
cam.rotation_euler = (target-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type = "ORTHO"
cam.data.ortho_scale = 3.55
bpy.context.scene.camera = cam

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.render.resolution_x = 1000
scene.render.resolution_y = 750
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT/"runner_prototype_preview.png")
scene.world.color = (.16,.18,.21)
scene.view_settings.view_transform = "Standard"

# Save the editable model even if the optional PNG render fails.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"runner_prototype.blend"))
try:
    bpy.ops.render.render(write_still=True)
except Exception as exc:
    print("WARNING: preview render unavailable:", repr(exc))

summary = {
    "prototype": "Four-eyed amphibious runner (not an approved game asset)",
    "mesh_parts": len(asset_objects),
    "eye_count": 4,
    "leg_count": 4,
    "blender_version": bpy.app.version_string,
    "formats": ["glb", "blend", "png if rendering succeeds"],
    "units": "meters",
}
(OUT/"runner_prototype_info.json").write_text(json.dumps(summary,indent=2))
assert (OUT/"runner_prototype.glb").stat().st_size > 1024
assert (OUT/"runner_prototype.blend").stat().st_size > 1024
print("CLOUD_BLENDER_SUCCESS", json.dumps(summary))
