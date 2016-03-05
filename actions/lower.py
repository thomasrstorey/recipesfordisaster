'''
lower.py

Takes a list of input ingredient names. Imports each if not already present.
Then takes the selected ingredient and lowers it.

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

def createMesh(name, origin, verts, faces):
    mesh = bpy.data.meshes.new(name+"Mesh")
    obj = bpy.data.objects.new(name, mesh)
    obj.location = origin
    obj.show_name = True
    scn = bpy.context.scene
    scn.objects.link(obj)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

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
    else:
        obj = bpy.data.objects[objname]
        return obj

def addGroundPlane(obj):
    faces = ((0,3,2,1),(0,1,5,4),(1,2,6,5),
          (3,7,6,2),(0,4,7,3),(4,5,6,7))
    (l, w, h) = (obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
    po = (obj.bound_box[0][0]+(l*0.5),
        obj.bound_box[0][1]+(w*0.5),
        obj.bound_box[0][2]-1)
    pv = ((l*10,l*10,1),(l*10,l*-10,1),(l*-10,l*-10,1),(l*-10,l*10,1),
        (l*10,l*10,-1),(l*10,l*-10,-1),(l*-10,l*-10,-1),(l*-10,l*10,-1))
    return createMesh("plane",po,pv,faces)

def addRigidbody(scn, obj, e, k, f):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.rigidbody.object_add(type='ACTIVE')
    obj.rigid_body.enabled = e
    obj.rigid_body.kinematic = k
    obj.rigid_body.friction = f
    obj.select = False

def removeRigidbody(scn, obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.object.visual_transform_apply()
    bpy.ops.rigidbody.object_remove()
    obj.select = False

def setOriginToGeometry(scn, obj):
    obj.select = True;
    scn.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
    obj.select = False;

def joinObjects(scn, objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select = True;
    activeobj = objs[0]
    scn.objects.active = activeobj
    bpy.ops.object.join()
    activeobj.name = name
    activeobj.data.name = name
    return activeobj

def lowerObject(obj):
    # define the translation
    loc_mat = Matrix.Translation((0.0,
                         0.0,
                         random.random()*-2.0))
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
    obj.matrix_world = loc_mat * orig_loc_mat * rot_mat * orig_rot_mat * orig_scale_mat

def execute(inputs, output):
    ctx = bpy.context
    scn = ctx.scene
    cwd = os.getcwd()
    objdir = os.path.join(cwd, 'objs')
    for objname in inputs:
        # import file, or get it if it's already here
        obj = getObject(objdir, objname)
        obj.location = Vector([0,0,0])
        lowerObject(obj)
        # # group dups together into one object
        copies = getObjectsBySubstring(objname)
        joined = joinObjects(scn, copies, objname)
        setOriginToGeometry(scn,joined)

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
    print("lowered " + ", ".join(inputs))

if __name__ == "__main__":
    main()
