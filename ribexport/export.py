# This file is part of blender-rib-export.
#
# Copyright 2007-2009 Roland Kuck <blenderrib@roland.kuck.name>
#
# blender-rib-export is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# blender-rib-export is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# blender-rib-export.  If not, see <http://www.gnu.org/licenses/>.

import Blender
import math
import rib
import params
import config

def matrix_to_list(m):
    retval = []
    for i in xrange(0, 4):
        for j in xrange(0, 4):
            retval.append(m[i][j])
    return retval

def export_camera(hout, camera):
    if type(camera.getData()) == Blender.Types.CameraType:
        c = camera.getData()
        if c.getType() == 0:
            fov = 2.*math.atan(16./c.getLens())*180./math.pi
            hout.output("Projection", "perspective",  "fov",  [fov,])
        else:
            scale = 1./c.getScale()
            hout.output("Scale", scale, scale, 1.)
            hout.output("Projection", "orthographic")
        hout.output("Clipping", c.getClipStart(), c.getClipEnd())
    hout.output("Scale", 1., 1., -1.)
    hout.output("ConcatTransform", matrix_to_list(camera.matrixWorld.invert()))

def shader_params(properties, object):
    param_list = []
    for prop in properties:
        param = eval(str(properties[prop]), vars(params), {'self': object})
        param_list += param.inline(prop)
    return param_list


class Empty(object):

    def __init__(self, ob):
        super(Empty, self).__init__()
        self.ob = ob

    def initialize(self):
        pass

    def output(self, hout):
        self.transform_begin(hout)
        self.transform_end(hout)

    def cleanup(self):
        pass

    def transform_begin(self, hout):
        hout.output("AttributeBegin")
        hout.output("Transform", matrix_to_list(self.ob.getMatrix()))
        hout.output("CoordinateSystem", str(self.ob.name))

    def transform_end(self, hout):
        hout.output("AttributeEnd")


class Mesh(Empty):

    subdiv_switch = Blender.Modifier.Settings.RENDER

    def __init__(self, ob):
        super(Mesh, self).__init__(ob)
        self.is_subdiv = False

    def initialize(self):
        try:
            self.lastmod = self.ob.modifiers[len(self.ob.modifiers)-1]
            if (self.lastmod.type == Blender.Modifier.Types.SUBSURF
             and self.lastmod[Blender.Modifier.Settings.TYPES] == 0
             and self.lastmod[self.subdiv_switch]):
                self.is_subdiv = True
                self.lastmod[self.subdiv_switch] = 0
        except:
            pass

    def output_surface_shader(self, hout):
        try:
            if (self.ob.colbits & 1) == 0:
                mat = self.ob.data.materials[0]
            else:
                mat = self.ob.getMaterials()[0]

            hout.output("Color", mat.rgbCol)

            ribdata = mat.properties[config.property_group]
            surface_shader = ribdata['Surface']
            surface_params = ribdata['SurfaceParams']
            param_list = shader_params(surface_params, mat)
            hout.output("Surface", surface_shader, *param_list)
        except:
            pass

    def output_mesh(self, hout):
        me = Blender.Mesh.New()
        me.getFromObject(self.ob, 0, 1)
        tokens = []

        if self.is_subdiv:
            cmd = "SubdivisionMesh"
            tokens.append("catmull-clark")
        else:
            cmd = "PointsPolygons"

        tokens.append(map(lambda f: len(f.v), me.faces))

        faces = []
        for f in me.faces:
            for v in f.v:
                faces.append(v.index)
        tokens.append(faces)

        # TODO We do not support tags for sudivisions yet, so just add empty lists
        if self.is_subdiv:
            tokens += [ [], [], [], [] ]

        tokens.append("P")
        points = []
        for v in me.verts:
            points += [ v.co[0], v.co[1], v.co[2] ]
        tokens.append(points)

        tokens.append("facevarying normal N")
        normals = []
        for f in me.faces:
            if f.smooth:
                for v in f.v:
                    normals += [ v.no[0], v.no[1], v.no[2] ]
            else:
                normals += len(f.v) * [ f.no[0], f.no[1], f.no[2] ]
        tokens.append(normals)

        hout.output(cmd, *tokens)

    def output(self, hout):
        self.transform_begin(hout)
        self.output_surface_shader(hout)
        self.output_mesh(hout)
        self.transform_end(hout)

    def cleanup(self):
        if self.is_subdiv:
            self.lastmod[self.subdiv_switch] = 1


class Light(Empty):

    def __init__(self, ob, light_handle, isglobal=False):
        super(Light, self).__init__(ob)
        self._light = light_handle
        self._isglobal = isglobal
        self._isvalid = True

    def output_lightsource_shader(self, hout):
        try:
            ribdata = self.ob.properties[config.property_group]
            lightsource_shader = ribdata['LightSource']
            lightsource_params = ribdata['LightSourceParams']
            param_list = shader_params(lightsource_params, self.ob)
            hout.output("LightSource", lightsource_shader, self._light, *param_list)
            self._isvalid = True
        except:
            self._isvalid = False

    def output_illuminate(self, hout):
        if self._isvalid:
            hout.output("Illuminate", self._light, 1)

    def output(self, hout):
        self.transform_begin(hout)
        self.output_lightsource_shader(hout)
        self.transform_end(hout)
        if self._isglobal:
            self.output_illuminate(hout)


def node_factory(ob, nodes):
    ob_type = ob.getType()
    if ob_type == 'Mesh':
        nodes['renderables'].append(Mesh(ob))
    elif ob_type == 'Lamp':
        light_handle = len(nodes['global_lights'])+len(nodes['local_lights'])+1
        if (ob.data.mode & Blender.Lamp.Modes["Layer"]) == 0:
            nodes['global_lights'].append(Light(ob, light_handle, True))
        else:
            nodes['local_lights'].append(Light(ob, light_handle))
    else:
        nodes['renderables'].append(Empty(ob))


def output_screen_setup(hout, context):
    size_x = context.imageSizeX()
    size_y = context.imageSizeY()
    par = float(context.aspectRatioX()) / float(context.aspectRatioY())
    far = size_x * par / size_y
    hout.output("Format", size_x, size_y, par)
    if (far > 1.):
        hout.output("ScreenWindow", -1., 1., -1./far, 1./far)
    else:
        hout.output("ScreenWindow", -far, far, -1., 1.)

def collect_nodes(scene):
    nodes = { 'global_lights':[], 'local_lights':[], 'renderables':[] }
    for ob in scene.objects:
        node_factory(ob, nodes)
    
    for nodelist in nodes.itervalues():
        for node in nodelist:
            node.initialize()

    return nodes

def cleanup_nodes(nodes):
    for nodelist in nodes.itervalues():
        for node in nodelist:
            node.cleanup()

def output_frame(hout, frame, scene, nodes):
    hout.output("FrameBegin", frame)
    camera = scene.objects.camera
    export_camera(hout, camera)
    
    hout.output("WorldBegin")
    
    # Now output nodes
    for nodelist in nodes['global_lights'], nodes['local_lights']:
        for node in nodelist:
            node.output(hout)
    for node in nodes['renderables']:
        hout.output("AttributeBegin")
        for l in nodes['local_lights']:
            if (node.ob.Layers & l.ob.Layers) != 0:
                l.output_illuminate(hout)
        node.output(hout)
        hout.output("AttributeEnd")
    
    hout.output("WorldEnd")
    hout.output("FrameEnd")

def create_rib_handler(filename, context, cur_frame):
    hfile = open(filename, 'w')
    if context.motionBlur:
        hout = rib.MotionRIB(hfile, 2, 0., context.mblurFactor)
        start_frame = cur_frame+0
        end_frame = cur_frame+2
    else:
        hout = rib.RIB(hfile)
        start_frame = cur_frame+0
        end_frame = cur_frame+1
    return hout, start_frame, end_frame


def export(filename, scene):
    context = scene.getRenderingContext()
    cur_frame = Blender.Get('curframe')

    hout, start_frame, end_frame = create_rib_handler(filename, context, cur_frame)

    nodes = collect_nodes(scene)
    output_screen_setup(hout, context)

    for frame in xrange(start_frame, end_frame):
        Blender.Set('curframe', frame)
        output_frame(hout, frame, scene, nodes)

    cleanup_nodes(nodes)

    hout.close()
    Blender.Set('curframe', cur_frame)
