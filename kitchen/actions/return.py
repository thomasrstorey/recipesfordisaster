'''
remove.py

Takes a list of input ingredient names. If this ingredient is present in the
scene, delete it. Otherwise do nothing.

DUPLICATE OF DISCARD.PY

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
    obj = bpy.data.objects.get(objname)
    return obj

def deleteObject(obj):
    bpy.context.scene.objects.unlink(obj)
    obj.user_clear()
    bpy.data.objects.remove(obj)

def execute(inputs, output):
    ctx = bpy.context
    scn = ctx.scene
    cwd = os.getcwd()
    objdir = os.path.join(cwd, 'objs')
    for objname in inputs:
        # get object if it's already here
        obj = getObject(objdir, objname)
        if not obj == None:
            deleteObject(obj)
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
    print("returned " + ", ".join(inputs))

if __name__ == "__main__":
    main()
