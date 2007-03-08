import Blender
import math
import rib
import params

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
        param = eval(str(properties[prop]), {}, vars(params)) #, {'self': object})
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
    subdiv_switch = Blender.Modifier.Settings.REALTIME  # BUG in Blender

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
            mat = self.ob.getMaterials()[0]
            ribdata = mat.properties['RIB']
            surface_shader = ribdata['Surface']
            surface_params = ribdata['SurfaceParams']
            param_list = shader_params(surface_params, mat)
            hout.output("Surface", surface_shader, *param_list)
        except:
            pass

    def output_mesh(self, hout):
        me = Blender.Mesh.New()
        #syime.getFromObject(self.ob, 0, 1)  # BUG in Blender
        me.getFromObject(self.ob, 0)
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
        if self.is_subdiv:
            tokens += [ [], [], [], [] ]
        tokens.append("P")
        points = []
        for v in me.verts:
            points += [ v.co[0], v.co[1], v.co[2] ]
        tokens.append(points)
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

    light_count = 0

    def __init__(self, ob):
        super(Light, self).__init__(ob)
        self.light_count += 1
        self.light = self.light_count

    def output_lightsource_shader(self, hout):
        try:
            ribdata = self.ob.properties['RIB']
            lightsource_shader = ribdata['LightSource']
            lightsource_params = ribdata['LightSourceParams']
            param_list = shader_params(lightsource_params, self.ob)
            hout.output("LightSource", lightsource_shader, self.light, *param_list)
        except:
            pass

    def output(self, hout):
        self.transform_begin(hout)
        self.output_lightsource_shader(hout)
        self.transform_end(hout)


def node_factory(ob, lights, renderables):
    ob_type = ob.getType()
    if ob_type == 'Mesh':
        renderables.append(Mesh(ob))
    elif ob_type == 'Lamp':
        lights.append(Light(ob))
    else:
        renderables.append(Empty(ob))


# Retrieve current scene
scene = Blender.Scene.GetCurrent()

# Create list of lights and renderable objects
lights = []
renderables = []
for ob in scene.getChildren():
    node_factory(ob, lights, renderables)

# Change blender state to faciliate export
for nodelist in lights, renderables:
    for node in nodelist:
        node.initialize()

# Output header
hout = rib.RIB(open('output.rib', 'w'))
context = scene.getRenderingContext()
size_x = context.imageSizeX()
size_y = context.imageSizeY()
par = float(context.aspectRatioX()) / float(context.aspectRatioY())
far = size_x * par / size_y
hout.output("Format", size_x, size_y, par)
if (far > 1.):
    hout.output("ScreenWindow", -1., 1., -1./far, 1./far)
else:
    hout.output("ScreenWindow", -far, far, -1., 1.)

hout.output("FrameBegin", 0)
camera = scene.getCurrentCamera()
export_camera(hout, camera)

hout.output("WorldBegin")

# Now output nodes
for node in lights:
    node.output(hout)
for node in renderables:
    hout.output("AttributeBegin")
    for l in lights:
        if (node.ob.Layers & l.ob.Layers) != 0:
            hout.output("Illuminate", l.light, 1)
    node.output(hout)
    hout.output("AttributeEnd")

hout.output("WorldEnd")
hout.output("FrameEnd")
hout.close()

# Change blender state to faciliate export
for nodelist in lights, renderables:
    for node in nodelist:
        node.cleanup()

