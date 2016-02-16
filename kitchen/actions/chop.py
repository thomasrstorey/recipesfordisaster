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

def execute(inputs, outputs):

    cwd = os.getcwd()
    scn = bpy.context.scene
    objdir = os.path.join(cwd, 'objs')
    for objname, outname in zip(inputs, outputs):
        objpath = os.path.join(objdir, objname)
        bpy.ops.import_scene.obj(filepath=objpath,axis_forward='Y',axis_up='Z')
        obj = bpy.data.objects[0]
        # number of times to divide bounding box
        div = 3
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
            dups.append(dup)
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
            # delete cells
            deleteObject(cell)
            set_uvs(dup.data)

        # add a plane under the cells
        po = (obj.bound_box[0][0]+(l*0.5), obj.bound_box[0][1]+(w*0.5), obj.bound_box[0][2]-1)
        pv = ((l*10,l*10,1),(l*10,l*-10,1),(l*-10,l*-10,1),(l*-10,l*10,1),
            (l*10,l*10,-1),(l*10,l*-10,-1),(l*-10,l*-10,-1),(l*-10,l*10,-1))
        plane = createMesh("plane",po,pv,faces)

        # delete original object
        deleteObject(obj)

        # add 'Animated' rigidbody to plane
        print(scn.rigidbody_world)
        bpy.ops.rigidbody.world_add()

        scn.rigidbody_world.group = bpy.data.groups.new("rigidbodies")
        scn.rigidbody_world.group.objects.link(plane)
        scn.update()
        bpy.ops.object.select_all(action='DESELECT')
        plane.select = True
        bpy.context.scene.objects.active = plane
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        plane.rigid_body.enabled = False
        plane.rigid_body.kinematic = True
        plane.rigid_body.friction = 0.750
        plane.select = False
        # # for each cell, add a 'Dynamic' rigidbody
        for dup in dups:
            dup.select = True;
            bpy.context.scene.objects.active = dup
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
            scn.rigidbody_world.group.objects.link(dup)
            bpy.ops.rigidbody.object_add(type='ACTIVE')
            dup.rigid_body.friction = 0.950
            dup.select = False;

        # # bake simulation and apply result
        bpy.ops.ptcache.bake_all(bake=True)
        scn.frame_current = scn.frame_end
        scn.frame_set(scn.frame_end)
        # # group dups together into one object
        bpy.ops.object.select_all(action='DESELECT')
        for dup in dups:
            dup.select = True;
        scn.objects.active = dups[0]
        bpy.ops.object.join()
        # # export duplicates as obj group
        outpath = os.path.join(objdir, outname)
        bpy.ops.export_scene.obj(filepath=outpath,check_existing=False,use_selection=True)

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

def main():
    import sys
    import argparse

    argv = sys.argv
    if "--" not in argv:
        argv = []
    else:
        argv = argv[argv.index("--") + 1:]
    usage_text =\
    "Usage: blender --background kitchen.blend --python " + __file__ + " -- "
    "[options]"
    parser = argparse.ArgumentParser(description=usage_text)
    parser.add_argument("-i", "--input", dest="input", type=str, required=True,
            help="Comma delimited list of .objs to import.")
    parser.add_argument("-o", "--output", dest="output", type=str, required=True,
            help="Comma delimited list of paths to export to,"
            " in order corresponding to inputs")
    args = parser.parse_args(argv)
    if not argv:
        parser.print_help()
        return
    if not args.input:
        print("input argument not given. aborting.")
        parser.print_help()
        return

    inputs = args.input.split(",")
    outputs = []
    if args.output:
        outputs = args.output.split(",")
    else:
        for inp in inputs:
            outp = inp[0:inp.index(".obj")]+"_chop.obj"
            outputs.append(inp+"_chop")
    execute(inputs, outputs)
    print("chopped " + ", ".join(inputs))

if __name__ == "__main__":
    main()
