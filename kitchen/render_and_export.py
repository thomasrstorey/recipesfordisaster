'''
render_and_export.py

open dish.blend
gather all objects together into one object, named <title> (provided as arg)
uv unwrap
bake all textures to one texture
set up  three cameras and three-point lighting
render three images
export dish to <title>.obj + <title>.mtl + <title>_color.jpg (path provided
as arg)

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


def joinScene(scn, title):
    # ensure all images are explicitly mapped to orignal UVs
    for obj in bpy.data.objects:
        for tex_slot in obj.material_slots[0].material.texture_slots:
            if tex_slot != None and tex_slot.texture.type == "IMAGE":
                tex_slot.texture_coords = "UV"
                tex_slot.uv_layer = "UVMap"

    # join all objects, center it and name it
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    scn.objects.active = bpy.data.objects[0]
    bpy.ops.object.join()
    obj = bpy.data.objects[0]
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
    obj.location = (0.0, 0.0, 0.0)
    obj.name = title

def uvUnwrap(scn, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")

    bakeUV = obj.data.uv_textures.new(name="bakeUV")
    for uv in obj.data.uv_textures:
        uv.active_render = False
    bakeUV.active_render = True
    obj.data.uv_textures.active_index = 1
    bpy.ops.uv.smart_project()

    bpy.ops.object.mode_set(mode="OBJECT")

def bakeTexture(scn, obj, title):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")

    bpy.ops.image.new()
    bakeImg = bpy.data.images["Untitled"]
    bakeImg.name = title + "_color"
    bpy.data.scenes["Scene"].render.bake_type = "TEXTURE"

    for area in bpy.context.screen.areas :
        if area.type == 'IMAGE_EDITOR' :
            area.spaces.active.image = bakeImg
    bpy.ops.object.bake_image()

    bpy.ops.object.mode_set(mode="OBJECT")
    return bakeImg

def export(scn, obj, img, title, opath):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    # clean up materials
    for mat_slot in obj.material_slots:
        if mat_slot != None:
            mat_slot.material.use_textures = (True, False, False, False,
             False, False, False, False, False, False, False, False,
              False, False, False, False, False, False)
            tex_slot = mat_slot.material.texture_slots[0]
            tex_slot.uv_layer = "bakeUV"
            tex_slot.texture.image = img

    # export baked image
    for area in bpy.context.screen.areas :
        if area.type == 'IMAGE_EDITOR' :
            area.spaces.active.image = img

    scn.render.image_settings.file_format='JPEG'
    img.save_render(opath+img.name+".jpg", scn)
    img.filepath = opath+img.name+".jpg"
    img.source = "FILE"
    # bpy.ops.image.save_as(filepath=opath+img.name+".jpg",check_existing=False)
    # export obj and mtl
    bpy.ops.export_scene.obj(filepath=opath+title+".obj",check_existing=False)

def execute(title, ipath, opath):
    ctx = bpy.context
    scn = ctx.scene
    joinScene(scn, title)
    obj = bpy.data.objects.get(title)
    uvUnwrap(scn, obj)
    img = bakeTexture(scn, obj, title)
    export(scn, obj, img, title, opath)
    # render(scn, obj, title, ipath)

def main():
    argv = sys.argv
    if "--" not in argv:
        argv = []
    else:
        argv = argv[argv.index("--") + 1:]
    usage_text =\
    "Usage: blender -b dish.blend --python " + __file__ + " -- [options]"
    parser = argparse.ArgumentParser(description=usage_text)
    parser.add_argument("-t", "--title", dest="title", type=str, required=True,
    help="Title of the recipe.")
    parser.add_argument("-ip", "--imagepath", dest="ipath", type=str, required=False,
    help="Path for rendered images.")
    parser.add_argument("-op", "--objectpath", dest="opath", type=str, required=False,
    help="Path for obj, mtl, and jpg.")
    args = parser.parse_args(argv)
    output = ""
    if not argv:
        parser.print_help()
        return
    if not args.title and args.ipath and args.opath:
        print("input argument not given. aborting.")
        parser.print_help()
        return


    execute(args.title, args.ipath, args.opath)
    print("served " + args.title)

if __name__ == "__main__":
    main()
