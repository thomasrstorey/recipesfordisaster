'''
sprinkle.py

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
    div = 8
    # dimensions of bounding box
    (l, w, h) = (obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
    # dimensions of cells
    (cl, cw, ch) = (l/div, w/div, h/div)
    # position of first cell
    cpos = (obj.bound_box[0][0]+cl*0.5,
         obj.bound_box[0][1]+cw*0.5,
         obj.bound_box[0][2]+ch*0.5)
    # cell faces
    faces = ((0,3,2,1),(0,1,5,4),(1,2,6,5),
          (3,7,6,2),(0,4,7,3),(4,5,6,7))
    # cells which will be used to chop the object
    cells = []
    for z in range(div):
        for y in range(div):
            for x in range(div):
                origin = (cpos[0]+(cl*x), cpos[1]+(cw*y), cpos[2]+(ch*z))

                verts = (( (cl/2),  (cw/2),  (ch/2)), #0
                      ( (cl/2), -(cw/2),  (ch/2)), #1
                      (-(cl/2), -(cw/2),  (ch/2)), #2
                      (-(cl/2),  (cw/2),  (ch/2)), #3
                      ( (cl/2),  (cw/2), -(ch/2)), #4
                      ( (cl/2), -(cw/2), -(ch/2)), #5
                      (-(cl/2), -(cw/2), -(ch/2)), #6
                      (-(cl/2),  (cw/2), -(ch/2))) #7
                cells.append(createMesh("cell", origin, verts, faces))
    return cells

def chop(scn, obj, cells):
    # for each cell, make a duplicate of the object
    dups = []
    dup = obj.copy()
    dup.data = obj.data.copy()
    scn.objects.link(dup)
    # add a boolean intersection modifier
    mod = dup.modifiers.new('intersection', 'BOOLEAN')
    mod.object = cells[0]
    mod.operation = 'INTERSECT'
    # apply modifier
    dup.data = dup.to_mesh(scn, True, 'RENDER')
    scn.update()
    dup.modifiers.remove(mod)
    deleteObject(dup)

    for cell in cells:
        dup = obj.copy()
        dup.data = obj.data.copy()
        scn.objects.link(dup)
        # add a boolean intersection modifier
        mod = dup.modifiers.new('intersection', 'BOOLEAN')
        mod.object = cell
        mod.operation = 'INTERSECT'
        # apply modifier
        dup.data = dup.to_mesh(scn, True, 'RENDER')
        scn.update()
        dup.modifiers.remove(mod)
        if len(dup.data.vertices) <= 0:
            # if after modifier, duplicate has zero verts, delete it
            deleteObject(dup)
        else:
            dups.append(dup)
            set_uvs(dup.data)
        # delete cells
        deleteObject(cell)

    return dups

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

def addRigidbody(scn, obj, e, k, f, cs):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scn.objects.active = obj
    bpy.ops.rigidbody.object_add(type='ACTIVE')
    obj.rigid_body.enabled = e
    obj.rigid_body.kinematic = k
    obj.rigid_body.friction = f
    obj.rigid_body.collision_shape = cs
    obj.rigid_body.collision_margin = 0.200
    if cs == 'MESH':
        obj.rigid_body.mesh_source = 'BASE'
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
        # add a plane under the cells
        plane = addPlate(obj)
        # delete original object
        deleteObject(obj)
        # ensure we are at the beginning of the timeline
        scn.frame_current = scn.frame_start
        scn.frame_set(scn.frame_start)
        # add 'Animated' rigidbody to plane
        try:
            bpy.ops.rigidbody.world_add()
        except RuntimeError:
            pass
        scn.rigidbody_world.group = bpy.data.groups.new("rigidbodies")
        addRigidbody(scn, plane, False, True, 0.150, 'MESH')
        scn.update()

        # # for each cell, add a 'Dynamic' rigidbody
        for chunk in chopped:
            setOriginToGeometry(scn, chunk)
            addRigidbody(scn, chunk, True, False, 0.150, 'CONVEX_HULL')

        # # bake simulation and apply result
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.ptcache.bake_all(bake=True)
        scn.frame_current = scn.frame_end
        scn.frame_set(scn.frame_end)
        for chunk in chopped:
            removeRigidbody(scn, chunk)
        # # group dups together into one object
        joined = joinObjects(scn, chopped, objname)
        setOriginToGeometry(scn,joined)
        joined.location = Vector([0,0,0])
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
    print("sprinkled " + ", ".join(inputs))

if __name__ == "__main__":
    main()
