import Blender
import math


def matrix_to_string(m):
    retval = '[ '
    for i in xrange(0, 4):
        for j in xrange(0, 4):
            retval += str(m[i][j]) + ' '
    retval += ']'
    return retval


def export_mesh(hout, ob, props):
    subdiv = props.get('SubDiv', False)
    me = ob.getData()
    if subdiv:
        print >> hout, 'SubdivisionMesh "catmull-clark" [',
    else:
        print >> hout, 'PointsPolygons [',
    for f in me.faces:
        print >> hout, len(f.v),
    print >> hout, '] [',
    for f in me.faces:
        for v in f.v:
            print >> hout, v.index,
    print >> hout, ']',
    if subdiv:
        print >> hout, ' [] [] [] []',
    print >> hout, ' "P" [',
    for v in me.verts:
        print >> hout, v.co[0], v.co[1], v.co[2],
    print >> hout, ']'
        

def export_camera(hout, camera):
    if type(camera.getData()) == Blender.Types.CameraType:
        c = camera.getData()
        if c.getType() == 0:
            fov = 2.*math.atan(16./c.getLens())*180./math.pi
            print >> hout, 'Projection "perspective" "fov" ['+str(fov)+']'
        else:
            scale = 1./c.getScale()
            print >> hout, 'Scale ' + str(scale) + ' ' + str(scale) + ' 1.'
            print >> hout, 'Projection "orthographic"'
        print >> hout, 'Clipping', c.getClipStart(), c.getClipEnd()
    print >> hout, 'Scale 1. 1. -1.'
    print >> hout, 'ConcatTransform', matrix_to_string(camera.matrixWorld.invert())


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
        
        print >> hout, 'CoordinateSystem "'+str(n.ob.name)+'"'
        print >> hout, 'AttributeBegin'
        print >> hout, 'Transform', matrix_to_string(n.ob.getMatrix())

        surface = props.get('Surface', None)
        if (surface != None) and (len(surface) != 0):
            print >> hout, 'Surface "'+str(surface)+'"'

        if type(n.ob.getData()) == Blender.Types.NMeshType:
            export_mesh(hout, n.ob, props)
        recurse_transform(hout, n.children)
        
        print >> hout, 'AttributeEnd'


# Output header
hout = open('output.rib', 'w')
context = scene.getRenderingContext()
size_x = context.imageSizeX()
size_y = context.imageSizeY()
par = float(context.aspectRatioX()) / float(context.aspectRatioY())
far = size_x * par / size_y
print >> hout, 'Format', size_x, size_y, par
if (far > 1.):
    print >> hout, 'ScreenWindow -1 1', -1./far, 1./far
else:
    print >> hout, 'ScreenWindow', -far, far, '-1 1'
print >> hout, 'FrameBegin 0'
export_camera(hout, camera)
print >> hout, 'WorldBegin'
recurse_transform(hout, root)		
print >> hout, 'WorldEnd'
print >> hout, 'FrameEnd'
