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
        try:
            def Float(f):
                return f
            mat = self.ob.getMaterials()[0]
            ribdata = mat.properties['RIB']
            surface_shader = ribdata['Surface']
            surface_params = ribdata['SurfaceParams']
            param_list = []
            for prop in surface_params:
                param = eval(str(surface_params[prop]), {}, vars(params))
                param_list += param.inline(prop)
            hout.output("Surface", surface_shader, *param_list)
        except:
            pass

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
            if self.lastmod.type == Blender.Modifier.Types.SUBSURF \
             and self.lastmod[Blender.Modifier.Settings.TYPES] == 0 \
             and self.lastmod[self.subdiv_switch]:
                self.is_subdiv = True
                self.lastmod[self.subdiv_switch] = 0
        except:
            pass

    def output(self, hout):
        self.transform_begin(hout)
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
        self.transform_end(hout)

    def cleanup(self):
        if self.is_subdiv:
            self.lastmod[self.subdiv_switch] = 1


class Light(Empty):
    def __init__(self, ob):
        super(Light, self).__init__(ob)

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
for node in lights:
    node.initialize()
for node in renderables:
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
    node.output(hout)

hout.output("WorldEnd")
hout.output("FrameEnd")
hout.close()

# Change blender state to faciliate export
for node in lights:
    node.cleanup()
for node in renderables:
    node.cleanup()

