import Blender
import math
import rib


def matrix_to_list(m):
    retval = []
    for i in xrange(0, 4):
        for j in xrange(0, 4):
            retval.append(m[i][j])
    return retval


def export_mesh(hout, ob, props):
    subdiv = props.get('SubDiv', False)
    me = ob.getData()
    tokens = []
    if subdiv:
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
    if subdiv:
        tokens += [ [], [], [], [] ]
    tokens.append("P")
    points = []
    for v in me.verts:
        points += [ v.co[0], v.co[1], v.co[2] ]
    tokens.append(points)
    hout.output(cmd, *tokens)
        

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


# Trivial node class
class node(object):
    def __init__(self, ob):
        super(node,self).__init__()
        self.ob = ob
        self.children = []

# Get current scene and camera
scene = Blender.Scene.getCurrent()
camera = scene.getCurrentCamera()

# Iterate over all objects in scene and build hierarchy
#  As blender object are not hashable type we use their names
#  instead (which are guaranteed to be unique)
root = []
dict = {}
for ob in scene.getChildren():
    n = node(ob)
    dict[ob.name] = n
for n in dict.itervalues():
    parent = n.ob.getParent()
    if (parent == None):
        root.append(n)
    else:
        dict[parent.name].children.append(n)

# Recurse and print meshes
def recurse_transform(hout, nodelist):
    for n in nodelist:
        props = {}
        props_list = n.ob.getAllProperties()
        for p in props_list:
            props[p.getName()] = p.getData() 
        
        hout.output("CoordinateSystem", str(n.ob.name))
        hout.output("AttributeBegin")
        hout.output("Transform", matrix_to_list(n.ob.getMatrix()))

        surface = props.get('Surface', None)
        if (surface != None) and (len(surface) != 0):
            hout.output("Surface", str(surface))

        if type(n.ob.getData()) == Blender.Types.NMeshType:
            export_mesh(hout, n.ob, props)
        recurse_transform(hout, n.children)
        
        hout.output("AttributeEnd")


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
export_camera(hout, camera)
hout.output("WorldBegin")
recurse_transform(hout, root)		
hout.output("WorldEnd")
hout.output("FrameEnd")
