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

import unittest
import cStringIO
import parse

import rib

class TestRIB(unittest.TestCase):

    def testOutput(self):
        hin = cStringIO.StringIO()
        hout = rib.RIB(hin)
        hout.output("WorldBegin")
        hout.close()
        tokens = parse.parse(hin.getvalue())
        self.assertEqual([["WorldBegin"]], tokens)

    def testParamters(self):
        hin = cStringIO.StringIO()
        hout = rib.RIB(hin)
        hout.output("Option", "points", [1., 2., 3.])
        hout.close()
        tokens = parse.parse(hin.getvalue())
        self.assertEqual([["Option", "points", "[", 1., 2., 3., "]"]], tokens)

    def testHierarchy(self):
        hin = cStringIO.StringIO()
        hout = rib.RIB(hin)
        hout.output("WorldBegin")
        hout.output("TransformBegin")
        hout.output("Color")
        hout.output("Color")
        hout.output("TransformEnd")
        hout.output("TransformBegin")
        hout.output("TransformEnd")
        hout.output("WorldEnd")
        hout.close()
        self.assertEqual("WorldBegin\n  TransformBegin\n    Color\n    Color\n  TransformEnd\n  TransformBegin\n  TransformEnd\nWorldEnd", hin.getvalue())

    def testRiMethods(self):
        hin = cStringIO.StringIO()
        hout = rib.RIB(hin)
        hout.RiWorldBegin()
        hout.RiOption("points", [1., 2., 3.])
        hout.close()
        tokens = parse.parse(hin.getvalue())
        self.assertEqual([["WorldBegin"], ["Option", "points", "[", 1., 2., 3., "]"]], tokens)

    def testMotion(self):
        hin = cStringIO.StringIO()
        hout = rib.MotionRIB(hin, 3, 0., 1.)
        for i in xrange(0, 3):
            hout.RiFrameBegin(i)
            hout.RiTranslate(i, 0, 0)
            hout.RiColor([1., 0., 0.])
            hout.RiFrameEnd()
        hout.close()
        tokens = parse.parse(hin.getvalue())
        expected = [ ["Shutter", 0., 1.],
                     ["FrameBegin", 0.], 
                     ["MotionBegin", '[', 0., 0.5, 1., ']' ],
                     ["Translate", 0., 0., 0.],
                     ["Translate", 1., 0., 0.],
                     ["Translate", 2., 0., 0.],
                     ["MotionEnd"],
                     ["Color", '[', 1., 0., 0., ']' ],
                     ["FrameEnd"] ]
        self.assertEqual(expected, tokens)

    def testMotion2(self):
        hin = cStringIO.StringIO()
        hout = rib.MotionRIB(hin, 3, 0., 1.)
        for i in xrange(0, 5):
            hout.RiFrameBegin(i)
            hout.RiTranslate(i, 0, 0)
            hout.RiColor([1., 0., 0.])
            hout.RiFrameEnd()
        hout.close()
        tokens = parse.parse(hin.getvalue())
        expected = [ ["Shutter", 0., 1.],
                     ["FrameBegin", 0.], 
                     ["MotionBegin", '[', 0., 0.5, 1., ']' ],
                     ["Translate", 0., 0., 0.],
                     ["Translate", 1., 0., 0.],
                     ["Translate", 2., 0., 0.],
                     ["MotionEnd"],
                     ["Color", '[', 1., 0., 0., ']' ],
                     ["FrameEnd"],
                     ["Shutter", 1., 2.],
                     ["FrameBegin", 1.], 
                     ["MotionBegin", '[', 1., 1.5, 2., ']' ],
                     ["Translate", 2., 0., 0.],
                     ["Translate", 3., 0., 0.],
                     ["Translate", 4., 0., 0.],
                     ["MotionEnd"],
                     ["Color", '[', 1., 0., 0., ']' ],
                     ["FrameEnd"] ]
        self.assertEqual(expected, tokens)

class TestFormatter(unittest.TestCase):

    def setUp(self):
        self.hin = cStringIO.StringIO()
        self.hout = rib.Formatter(self.hin)

    def testEmpty(self):
        self.hout.close()
        self.assertEqual("", self.hin.getvalue())

    def testOneLine(self):
        self.hout.output("A")
        self.hout.close()
        self.assertEqual("A", self.hin.getvalue())

    def testMultipleLines(self):
        self.hout.output("A")
        self.hout.newline()
        self.hout.output("B")
        self.hout.newline()
        self.hout.output("C")
        self.hout.close()
        self.assertEqual("A\nB\nC", self.hin.getvalue())

    def testTabs(self):
        self.hout.tabsize(2)
        self.hout.output("A")
        self.hout.indent()
        self.hout.newline()
        self.hout.output("B")
        self.hout.indent(-1)
        self.hout.newline()
        self.hout.output("C")
        self.hout.close()
        self.assertEqual("A\n  B\nC", self.hin.getvalue())

    def testWrap(self):
        self.hout.tabsize(1)
        self.hout.width(5)
        for x in xrange(0, 3):
            self.hout.output("A")
        self.hout.output("B")
        self.hout.split()
        self.hout.output("C")
        self.hout.output("C")
        self.hout.newline()
        self.hout.output("D")
        self.hout.close()
        self.assertEqual("A A A\n B\n C C\nD", self.hin.getvalue())

def retrieveTestSuite():
    suiteRIB = unittest.TestLoader().loadTestsFromTestCase(TestRIB)
    suiteFormatter = unittest.TestLoader().loadTestsFromTestCase(TestFormatter)
    return [suiteRIB, suiteFormatter]

if __name__ == '__main__':
    unittest.main()
