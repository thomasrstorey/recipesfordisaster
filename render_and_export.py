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
    # duplicate a material to get around the obj rendering limitation in
    # ARToolkit...
    obj.data.materials.append(obj.material_slots[0].material)

    # export baked image
    for area in bpy.context.screen.areas :
        if area.type == 'IMAGE_EDITOR' :
            area.spaces.active.image = img

    scn.render.image_settings.file_format='JPEG'
    img.save_render(opath+img.name+".jpg", scn)
    img.filepath = opath+img.name+".jpg"
    img.source = "FILE"
    # export obj and mtl
    bpy.ops.export_scene.obj(filepath=opath+title+".obj",check_existing=False)

def createRenderCam(obj):
    cam = bpy.data.cameras.new("cam")
    cam_ob = bpy.data.objects.new("Cam", cam)
    bpy.context.scene.objects.link(cam_ob)
    # setup camera
    tt = cam_ob.constraints.new("TRACK_TO")
    tt.target = obj
    tt.track_axis = "TRACK_NEGATIVE_Z"
    tt.up_axis = "UP_Y"

    cam.dof_object = obj
    cam.cycles.aperture_type = "FSTOP"
    cam.cycles.aperture_fstop = 0.3
    cam_ob.location = ((random.random()-0.5)*16,
                (random.random()-0.5)*16,
                (random.random())*8)
    return cam_ob

def createPlate(obj):
    objdir = os.path.join(os.getcwd(), "objs")
    objpath = os.path.join(objdir, "renderPlate.obj")
    bpy.ops.import_scene.obj(filepath=objpath,axis_forward='Y',axis_up='Z')
    plate = bpy.data.objects.get("renderPlate")
    plate.location = (0.0,0.0,-0.25)
    plate_mat = plate.material_slots[0].material
    plate_mat.use_nodes = True
    plate_tree = plate_mat.node_tree
    plate_links = plate_tree.links
    plate_tree.nodes.clear()

    out = plate_tree.nodes.new("ShaderNodeOutputMaterial")
    add = plate_tree.nodes.new("ShaderNodeAddShader")
    mix = plate_tree.nodes.new("ShaderNodeMixShader")
    glossy = plate_tree.nodes.new("ShaderNodeBsdfGlossy")
    white = plate_tree.nodes.new("ShaderNodeBsdfDiffuse")
    black = plate_tree.nodes.new("ShaderNodeBsdfDiffuse")
    lw = plate_tree.nodes.new("ShaderNodeLayerWeight")

    plate_links.new(add.outputs[0], out.inputs[0])
    plate_links.new(mix.outputs[0], add.inputs[0])
    plate_links.new(glossy.outputs[0], add.inputs[1])
    plate_links.new(lw.outputs[1], mix.inputs[0])
    plate_links.new(white.outputs[0], mix.inputs[1])
    plate_links.new(black.outputs[0], mix.inputs[2])

    glossy.distribution = "BECKMANN"
    glossy.inputs[0].default_value = (0.3,0.3,0.3,1.0)
    glossy.inputs[1].default_value = 0.2

    lw.inputs[0].default_value = 0.1

    black.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

def render(scn, obj, title, ipath):
    cwd = os.getcwd()
    # setup ibl
    scn.render.engine = 'CYCLES'
    scn.cycles.samples = 200
    # convert object materials to cycles materials...
    for mat_slot in obj.material_slots:
        if mat_slot != None:
            mat_slot.material.use_nodes = True
            mat_tree = mat_slot.material.node_tree
            mat_links = mat_tree.links
            diffNode = mat_tree.nodes["Diffuse BSDF"]
            texImgNode = mat_tree.nodes.new("ShaderNodeTexImage")
            texImgNode.image = bpy.data.images[title+"_color"]
            mat_links.new(texImgNode.outputs[0], diffNode.inputs[0])
    # setup world
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    tree = world.node_tree
    links = tree.links
    bg = tree.nodes['Background']
    bg.inputs[1].default_value = 2.0

    bpy.ops.image.open(filepath=cwd+"/kitchen_envtex.hdr")
    envTexImg = bpy.data.images["kitchen_envtex.hdr"]

    envTex = tree.nodes.new('ShaderNodeTexEnvironment')
    envTex.image = envTexImg
    links.new(envTex.outputs[0], bg.inputs[0])

    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.vector_type = "TEXTURE"
    links.new(mapping.outputs[0], envTex.inputs[0])

    gen = tree.nodes.new("ShaderNodeTexCoord")
    links.new(gen.outputs[0], mapping.inputs[0])

    #setup plate
    createPlate(obj)

    # create cameras
    cam_ob = createRenderCam(obj)
    scn.camera = cam_ob
    # render three images
    scn.render.resolution_x = 720
    scn.render.resolution_y = 540
    scn.render.resolution_percentage = 100
    for fn in range(1,4):
        fp = ipath+title+str(fn)
        scn.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        cam_ob.location = ((random.random()-0.5)*(2*fn),
                    (random.random()-0.5)*(2*fn),
                    (random.random())*8)

def execute(title, ipath, opath):
    ctx = bpy.context
    scn = ctx.scene
    joinScene(scn, title)
    obj = bpy.data.objects.get(title)
    uvUnwrap(scn, obj)
    img = bakeTexture(scn, obj, title)
    export(scn, obj, img, title, opath)
    render(scn, obj, title, ipath)

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
    parser.add_argument("-ip", "--imagepath", dest="ipath", type=str,
    required=False, help="Path for rendered images.")
    parser.add_argument("-op", "--objectpath", dest="opath", type=str,
    required=False, help="Path for obj, mtl, and jpg.")
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
