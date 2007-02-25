import unittest
import parse

class TestParse(unittest.TestCase):

    def testParseNames(self):
        in_str = "One Two Three"
        in_tokens = [ ["One"], ["Two"], ["Three"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testParseNames_Space(self):
        in_str = " One   Two  Three"
        in_tokens = [ ["One"], ["Two"], ["Three"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testParseStrings(self):
        in_str = ' One "Two"  Three "Four"'
        in_tokens = [ ["One", "Two"], ["Three", "Four"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testParseNumber(self):
        in_str = 'Option "limits" 6'
        in_tokens = [ ["Option", "limits", 6 ] ]
        self.assertEqual(parse.parse(in_str), in_tokens)
        
    def testParseArray(self):
        in_str = 'Option "limits" "bucketsize" [6 6]'
        in_tokens = [ ["Option", "limits", "bucketsize", '[', 6, 6, ']' ] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testParseArray(self):
        in_str = 'One Two #Three\n Four'
        in_tokens = [ ["One"], ["Two"], ["Four"] ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testParseComplex(self):
        in_str = """Declare "squish" "uniform float"
Option "limits" "bucketsize" [6 6] #renderer specific
WorldBegin"""
        in_tokens = [ ["Declare", "squish", "uniform float"],
                      ["Option", "limits", "bucketsize", '[', 6, 6, ']' ],
                      ["WorldBegin"]
                    ]
        self.assertEqual(parse.parse(in_str), in_tokens)


def retrieveTestSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestParse) 

if __name__ == '__main__':
    unittest.main()
