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
