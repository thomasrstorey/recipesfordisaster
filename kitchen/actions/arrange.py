'''
arrange.py

Takes a list of input ingredient names. If there is more than one, arranges
each item in the list in a row, importing as necessary. If there is only one,
arrange next to another object in the scene. If the scene is empty and there's
only one argument, just set it at the origin.

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
    return bpy.data.objects[objname]

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

def arrange(anchor, obj, i, off, axis):
    if(axis == 'X'):
        obj.location = ([anchor.location.x + i * off,
                    anchor.location.y,
                    anchor.location.z])
    elif axis == 'Y':
        obj.location = ([anchor.location.x,
                    anchor.location.y + i * off,
                    anchor.location.z])
    elif axis == 'Z':
        obj.location = ([anchor.location.x,
                    anchor.location.y, 
                    anchor.location.z + i * off])

def execute(inputs, output):
    ctx = bpy.context
    scn = ctx.scene
    cwd = os.getcwd()
    objdir = os.path.join(cwd, 'objs')
    if len(inputs) > 1:
        # arrange each input next to each other
        # first put the first one at the origin
        objname = inputs[0]
        print("arranging " + objname)
        obj = getObject(objdir, objname)
        obj.location = Vector([0,0,0])
        # get narrowest dimension
        (l, w, h) = (obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
        offset = min(l,w,h)
        for objname, i in zip(inputs[1:], range(1, len(inputs))):
            print("arranging " + objname)
            if(offset == l):
                arrange(obj, getObject(objdir, objname), i, offset, 'X')
            elif(offset == w):
                arrange(obj, getObject(objdir, objname), i, offset, 'Y')
            else:
                arrange(obj, getObject(objdir, objname), i, offset, 'Z')
    elif len(bpy.data.objects) > 1:
        # select a random object and arrange the input next to it
        objname = inputs[0]
        print("arranging " + objname)
        obj = getObject(objdir, objname)
        anchor = None
        for other in bpy.data.objects:
            if other.name != objname:
                anchor = other
                break
        (l, w, h) = (anchor.dimensions.x,
                 anchor.dimensions.y,
                 anchor.dimensions.z)
        offset = min(l,w,h)
        if(offset == l):
            arrange(anchor, obj, 1, offset, 'X')
        elif(offset == w):
            arrange(anchor, obj, 1, offset, 'Y')
        else:
            arrange(anchor, obj, 1, offset, 'Z')
    else:
        # put input at the origin
        objname = inputs[0]
        print("arranging " + objname)
        obj = getObject(objdir, objname)
        obj.location = Vector([0,0,0])

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
    print("arranged " + ", ".join(inputs))

if __name__ == "__main__":
    main()
