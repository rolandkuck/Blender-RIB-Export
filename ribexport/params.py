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

class Point(_Float3):
    def __init__(self, *args):
        super(Point, self).__init__(*args)
        self.type = "point"

class Vector(_Float3):
    def __init__(self, *args):
        super(Vector, self).__init__(*args)
        self.type = "vector"

class Normal(_Float3):
    def __init__(self, *args):
        super(Normal, self).__init__(*args)
        self.type = "normal"

class Color(_Float3):
    def __init__(self, *args):
        super(Color, self).__init__(*args)
        self.type = "color"
