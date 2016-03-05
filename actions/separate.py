'''
chop.py

Takes a list of input ingredient names. Chops each ingredient, and adds the
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
        bpy.ops.import_scene.obj(filepath=objpath,axis_forward='Y',axis_up='Z')
    return bpy.data.objects[objname]

def generateChopGeometry(obj):
    # number of times to divide bounding box
    div = 2
    # dimensions of bounding box
    (l, w, h) = (obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
    # cell faces
    faces = ((0,3,2,1),(0,1,5,4),(1,2,6,5),
          (3,7,6,2),(0,4,7,3),(4,5,6,7))
    # dimensions of cells
    if(max(l, w, h) == l):
        # position of first cell
        cpos = (obj.location.x+l*0.25,
             obj.location.y,
             obj.location.z)
        (cl, cw, ch) = (l/2, w, h)
    elif(max(l, w, h) == w):
        cpos = (obj.location.x,
             obj.location.y+w*0.25,
             obj.location.z)
        (cl, cw, ch) = (l, w/2, h)
    elif(max(l, w, h) == h):
        cpos = (obj.location.x,
             obj.location.y,
             obj.location.z+h*0.25)
        (cl, cw, ch) = (l, w, h/2)
    verts = (( (cl/2),  (cw/2),  (ch/2)), #0
          ( (cl/2), -(cw/2),  (ch/2)), #1
          (-(cl/2), -(cw/2),  (ch/2)), #2
          (-(cl/2),  (cw/2),  (ch/2)), #3
          ( (cl/2),  (cw/2), -(ch/2)), #4
          ( (cl/2), -(cw/2), -(ch/2)), #5
          (-(cl/2), -(cw/2), -(ch/2)), #6
          (-(cl/2),  (cw/2), -(ch/2))) #7
    divider = createMesh("divider", cpos, verts, faces)
    return divider

def chop(scn, obj, divider):

    mod = obj.modifiers.new('difference', 'BOOLEAN')
    mod.object = divider
    mod.operation = 'DIFFERENCE'
    # apply modifier
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True;
    scn.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    scn.update()
    set_uvs(obj.data)
    deleteObject(divider)
    return obj

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

def set_uvs_for_face(bm, fi, uv_layer):
    face = bm.faces[fi]
    zv = Vector((0.0, 0.0))
    normal = face.normal
    dx=abs(normal[0])
    dy=abs(normal[1])
    dz=abs(normal[2])

    if (dz > dx):
        u = Vector([1,0,0])
        if (dz>dy):
            v = Vector([0,1,0])
        else:
            v = Vector([0,0,1])
    else:
        v = Vector([0,0,1])
        if dx>dy:
            u = Vector([0,1,0])
        else:
            u = Vector([1,0,0])
    for i in range(len(face.loops)):
        if(face.loops[i][uv_layer].uv == zv):
            l = face.loops[i]
            l[uv_layer].uv = [ u.dot(l.vert.co),v.dot(l.vert.co)]

def set_uvs(mesh):
    uv = mesh.uv_textures[0]
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv[uv.name]
    for fi in range(len(bm.faces)):
        set_uvs_for_face(bm, fi, uv_layer)
    bm.to_mesh(mesh)

def indexOfSubstring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1

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
        # import file, or get it if it's already here
        obj = getObject(objdir, objname)
        cells = generateChopGeometry(obj)
        chopped = chop(scn, obj, cells)

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
    print("separated " + ", ".join(inputs))

if __name__ == "__main__":
    main()
