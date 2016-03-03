'''
pour.py

Takes a list of input ingredient names. Melts each ingredient, and adds the
resulting model to the current blend or a new blend

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

def deleteObject(obj):
    bpy.context.scene.objects.unlink(obj)
    obj.user_clear()
    bpy.data.objects.remove(obj)

def getObject(objdir, objname):
    if (bpy.data.objects.get(objname) == None):
        objpath = os.path.join(objdir, objname+".obj")
        bpy.ops.import_scene.obj(filepath=objpath,axis_forward='Y',axis_up='Z')
    return bpy.data.objects[objname]

def addPlate(obj):
    cwd = os.getcwd()
    objdir = os.path.join(cwd, 'objs')
    objpath = os.path.join(objdir, "plate.obj")
    (l, w, h) = (obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
    po = (obj.bound_box[0][0]+(l*0.5),
        obj.bound_box[0][1]+(w*0.5),
        obj.bound_box[0][2]-1)
    bpy.ops.import_scene.obj(filepath=objpath,axis_forward='Z',axis_up='Y')
    plate = getObjectsBySubstring("Plate")[0]
    plate.location = po
    return plate

def addSoftbodyMod(scn, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.modifier_add(type='SOFT_BODY')
    obj.modifiers["Softbody"].settings.use_goal = False
    obj.modifiers["Softbody"].settings.use_self_collision = True
    obj.modifiers["Softbody"].settings.ball_size = 0.600
    obj.modifiers["Softbody"].settings.ball_stiff = 1.00
    obj.modifiers["Softbody"].settings.ball_damp = 0.800
    obj.select = False

def addClothMod(scn, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.modifier_add(type='CLOTH')
    obj.modifiers["Cloth"].point_cache.frame_end = 30
    obj.select = False

def removeMod(scn, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    obj.select = False

def addCollision(scn, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.modifier_add(type='COLLISION')
    obj.collision.thickness_inner = 0.100
    obj.select = False

def setOriginToGeometry(scn, obj):
    obj.select = True;
    scn.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
    obj.select = False;

def getObjectsBySubstring(objname):
    copies = []
    for obj in bpy.data.objects:
        if(objname in obj.name):
            copies.append(obj)
    return copies

def execute(inputs, output):
    ctx = bpy.context
    scn = ctx.scene
    cwd = os.getcwd()
    objdir = os.path.join(cwd, 'objs')
    for objname in inputs:
        print("pouring " + objname)
        # import file, or get it if it's already here
        obj = getObject(objdir, objname)
        # add a plane under the cells
        plane = addPlate(obj)
        # ensure we are at the beginning of the timeline
        scn.frame_current = scn.frame_start
        scn.frame_set(scn.frame_start)
        # add collision to plane
        addCollision(scn, plane)
        # add softbody to object

        addClothMod(scn, obj)
        # # bake simulation and apply result
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.ptcache.bake_all(bake=True)
        scn.frame_current = scn.frame_end
        scn.frame_set(scn.frame_end)
        removeMod(scn, obj)
        setOriginToGeometry(scn, obj)
        obj.location = Vector([0,0,0])
        # clean up - delete ground plane
        deleteObject(plane)

    # save out .blend
    if not output == None:
        bpy.ops.wm.save_as_mainfile(filepath=output,
        check_existing=False,relative_remap=False)
    else:
        bpy.ops.wm.save_mainfile(check_existing=False,relative_remap=False)

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
    print("poured " + ", ".join(inputs))

if __name__ == "__main__":
    main()
