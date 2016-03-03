'''
add.py

Takes a list of input ingredient names. Imports each if not already present.
If already present, duplicates and rotates the ingredient.

Thomas Storey
2016

'''

import sys
import argparse
import bpy
import numpy as np
import os
import bmesh
from math import *
from mathutils import *
import random

def getObjectsBySubstring(objname):
    copies = []
    for obj in bpy.data.objects:
        if(objname in obj.name):
            copies.append(obj)
    return copies

def deleteObject(obj):
    bpy.context.scene.objects.unlink(obj)
    obj.user_clear()
    bpy.data.objects.remove(obj)

def getObject(objdir, objname):
    if (bpy.data.objects.get(objname) == None):
        objpath = os.path.join(objdir, objname+".obj")
        bpy.ops.import_scene.obj(filepath=objpath,
                         axis_forward='Y',axis_up='Z')
    return bpy.data.objects[objname]

def setOriginToGeometry(scn, obj):
    obj.select = True;
    scn.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
    obj.select = False;

def joinObjects(scn, objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select = True
    activeobj = objs[0]
    scn.objects.active = activeobj
    bpy.ops.object.join()
    activeobj.name = name
    activeobj.data.name = name
    return activeobj

def bakeObject(scn, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    mat = obj.material_slots[0].material


    bpy.ops.texture.new()
    tex = bpy.data.textures["Texture"]
    tex.name = "bake"
    tex_slot = mat.texture_slots.add()
    tex_slot.texture = tex
    bpy.ops.image.new()
    img = bpy.data.images["Untitled"]
    img.name = "bake_img"
    tex.image = img
    img.generated_color = (0.073, 0.019, 0.010, 1.00)
    tex_slot.blend_type = 'SOFT_LIGHT'

    # bpy.ops.texture.new()
    # baked_tex = bpy.data.textures["Texture"]
    # baked_tex.name = "baked"
    # baked_tex_slot = mat.texture_slots.create(2)
    # baked_tex_slot.texture = baked_tex
    # bpy.ops.image.new()
    # baked_img = bpy.data.images["Untitled"]
    # baked_img.name = "baked_img"
    # mat.active_texture_index = 2
    # mat.active_texture = baked_tex
    #
    # bpy.ops.object.mode_set(mode="EDIT")
    # bpy.data.scenes["Scene"].render.bake_type = "TEXTURE"
    # for area in bpy.context.screen.areas :
    #     if area.type == 'IMAGE_EDITOR' :
    #         area.spaces.active.image = baked_img
    # bpy.ops.object.bake_image()
    # mat.texture_slots[0].texture.image = baked_img

def execute(inputs, output):
    ctx = bpy.context
    scn = ctx.scene
    cwd = os.getcwd()
    objdir = os.path.join(cwd, 'objs')
    for objname in inputs:
        # import file, or get it if it's already here
        obj = getObject(objdir, objname)
        obj.location = Vector([0,0,0])
        bakeObject(scn, obj)

    # save out .blend
    if not output == None:
        bpy.ops.wm.save_as_mainfile(filepath=output,
        check_existing=False,relative_remap=True)
    else:
        bpy.ops.wm.save_mainfile(check_existing=False,relative_remap=True)

def main():
    argv = sys.argv
    if "--" not in argv:
        argv = []
    else:
        argv = argv[argv.index("--") + 1:]
    usage_text =\
    "Usage: blender -b [.blend file] --python " + __file__ + " -- [options]"
    parser = argparse.ArgumentParser(description=usage_text)
    parser.add_argument("-i", "--input", dest="input", type=str, required=True,
    help="Comma delimited list of .objs to import. Exclude the file extension.")
    parser.add_argument("-o", "--output", dest="output", type=str, required=False,
    help="Name of blend file to save to, if not the same as the one being opened.")
    args = parser.parse_args(argv)
    output = ""
    if not argv:
        parser.print_help()
        return
    if not args.input:
        print("input argument not given. aborting.")
        parser.print_help()
        return
    if not args.output:
        output = None
    else:
        output = args.output+".blend"

    inputs = args.input.split(",")
    execute(inputs, output)
    print("baked " + ", ".join(inputs))

if __name__ == "__main__":
    main()
