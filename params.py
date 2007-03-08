#
# Imitate PyDrivers
#

import Blender
b = blender = Blender

import Blender.Noise as noise
n = noise

import math
m = math

ob = Blender.Object.Get
me = Blender.Mesh.Get
ma = Blender.Material.Get
la = Blender.Lamp.Get


#
# Define possible shader types
#

class _Parameter(object):
    def inline(self, name):
        return [ "uniform %s %s" % (self.type, str(name)), self.values ]

class Float(_Parameter):
    def __init__(self, value):
        self.values = [ float(value) ]
        self.type = "float"

class String(_Parameter):
    def __init__(self, value):
        self.values = [ str(value) ]
        self.type = "string"

class _Float3(_Parameter):
    def __init__(self, *args):
        try:
            if len(args) == 1:
                values = args[0]
            else:
                values = args
            if len(values) != 3:
                raise TypeError()
            self.values = [ float(v) for v in values ]
        except:
            raise TypeError()

class Vector(_Float3):
    def __init__(self, *args):
        super(Vector, self).__init__(*args)
        self.type = "vector"

class Normal(_Float3):
    def __init__(self, *args):
        super(Normal, self).__init__(*args)
        self.type = "normal"
