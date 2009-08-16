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
import parse

class TestParse(unittest.TestCase):

    def testNames(self):
        in_str = "One Two Three"
        in_tokens = [ ["One"], ["Two"], ["Three"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testNames_Space(self):
        in_str = " One   Two  Three"
        in_tokens = [ ["One"], ["Two"], ["Three"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testStrings(self):
        in_str = ' One "Two"  Three "Four"'
        in_tokens = [ ["One", "Two"], ["Three", "Four"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testNumber(self):
        in_str = 'Option "limits" 6'
        in_tokens = [ ["Option", "limits", 6 ] ]
        self.assertEqual(parse.parse(in_str), in_tokens)
        
    def testArray(self):
        in_str = 'Option "limits" "bucketsize" [6 6]'
        in_tokens = [ ["Option", "limits", "bucketsize", '[', 6, 6, ']' ] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testArray(self):
        in_str = 'One Two #Three\n Four'
        in_tokens = [ ["One"], ["Two"], ["Four"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testComplex(self):
        in_str = """Declare "squish" "uniform float"
Option "limits" "bucketsize" [6 6] #renderer specific
WorldBegin"""
        in_tokens = [ ["Declare", "squish", "uniform float"],
                      ["Option", "limits", "bucketsize", '[', 6, 6, ']' ],
                      ["WorldBegin"]
                    ]
        self.assertEqual(parse.parse(in_str), in_tokens)


class TestLineAssembler(unittest.TestCase):

    def testRetrieve(self):
        la = parse.LineAssembler()
        la.insert("A")
        la.insert("B")
        result = la.retrieve()
        self.assertEqual(result, [ ["A", "B"] ])

    def testRetrieve(self):
        la = parse.LineAssembler()
        la.insert("A")
        la.insert("B")
        la.flush()
        la.insert("C")
        result = la.retrieve()
        self.assertEqual(result, [ ["A", "B"], ["C"] ])


def retrieveTestSuite():
    suiteParse = unittest.TestLoader().loadTestsFromTestCase(TestParse)
    suiteLineAssembler = unittest.TestLoader().loadTestsFromTestCase(TestLineAssembler)
    return [suiteParse, suiteLineAssembler]

if __name__ == '__main__':
    unittest.main()
