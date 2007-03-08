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

class Float(object):
    def __init__(self, value):
        self.value = value
    def inline(self, name):
        return [ "uniform float %s" % str(name), [float(self.value)] ]
