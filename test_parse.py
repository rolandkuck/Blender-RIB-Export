import unittest
import parse

class TestParse(unittest.TestCase):

    def testParseNames(self):
        in_str = "One Two Three"
        in_tokens = [ ("One", None), ("Two", None), ("Three", None) ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testParseNames(self):
        in_str = " One   Two  Three "
        in_tokens = [ ("One", None), ("Two", None), ("Three", None) ]
        self.assertEqual(parse.parse(in_str), in_tokens)

    def testParseComplex(self):
        in_str = """Declare "squish" "uniform float"
Option "limits" "bucketsize" [6 6] #renderer specific
WorldBegin"""
        in_tokens = [ ("Declare", ["squish", "uniform float"]),
                      ("Option", ["limits", "bucketsize", [6, 6]]),
                      ("WorldBegin", None)
                    ]
        #self.assertEqual(parse.parse(in_str), in_tokens)


def retrieveTestSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestParse) 

if __name__ == '__main__':
    unittest.main()
