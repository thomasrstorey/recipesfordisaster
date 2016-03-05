'''
place.py

Takes a list of input ingredient names. Rotates and/or shifts each ingredient
slightly, importing it to the scene if it is not already there.

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

def getObject(objdir, objname):
    if (bpy.data.objects.get(objname) == None):
        objpath = os.path.join(objdir, objname+".obj")
        bpy.ops.import_scene.obj(filepath=objpath,
                         axis_forward='Y',axis_up='Z')
    else:
         deleteObject(bpy.data.objects.get(objname))
         objpath = os.path.join(objdir, objname+".obj")
         bpy.ops.import_scene.obj(filepath=objpath,
                          axis_forward='Y',axis_up='Z')
    return bpy.data.objects[objname]

def deleteObject(obj):
    bpy.context.scene.objects.unlink(obj)
    obj.user_clear()
    bpy.data.objects.remove(obj)

def rotateObjectRandomZ(obj):
    # define the rotation
    rot_mat = Matrix.Rotation(random.random()*pi*2, 4, 'Z')
    # decompose world_matrix's components, and from them assemble 4x4 matrices
    orig_loc, orig_rot, orig_scale = obj.matrix_world.decompose()
    orig_loc_mat = Matrix.Translation(orig_loc)
    orig_rot_mat = orig_rot.to_matrix().to_4x4()
    xscale = Matrix.Scale(orig_scale[0],4,(1,0,0))
    yscale = Matrix.Scale(orig_scale[1],4,(0,1,0))
    zscale = Matrix.Scale(orig_scale[2],4,(0,0,1))
    orig_scale_mat = xscale * yscale * zscale
    # assemble the new matrix
    obj.matrix_world = orig_loc_mat * rot_mat * orig_rot_mat * orig_scale_mat

def translateObjectRandomXY(obj):
    # define the translation
    loc_mat = Matrix.Translation(((random.random()-0.5)*2.0,
                         (random.random()-0.5)*2.0,
                         0.0))
    # decompose world_matrix's components, and from them assemble 4x4 matrices
    orig_loc, orig_rot, orig_scale = obj.matrix_world.decompose()
    orig_loc_mat = Matrix.Translation(orig_loc)
    orig_rot_mat = orig_rot.to_matrix().to_4x4()
    xscale = Matrix.Scale(orig_scale[0],4,(1,0,0))
    yscale = Matrix.Scale(orig_scale[1],4,(0,1,0))
    zscale = Matrix.Scale(orig_scale[2],4,(0,0,1))
    orig_scale_mat = xscale * yscale * zscale
    # assemble the new matrix
    obj.matrix_world = loc_mat * orig_rot_mat * orig_scale_mat

def execute(inputs, output):
    ctx = bpy.context
    scn = ctx.scene
    cwd = os.getcwd()
    objdir = os.path.join(cwd, 'objs')
    for objname in inputs:
        print("placing " + objname)
        # import file, or get it if it's already here
        obj = getObject(objdir, objname)
        obj.location = Vector([0,0,0])
        rotateObjectRandomZ(obj)
        translateObjectRandomXY(obj)

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
    print("placed " + ", ".join(inputs))

if __name__ == "__main__":
    main()
