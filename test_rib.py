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


def retrieveTestSuite():
    suiteRIB = unittest.TestLoader().loadTestsFromTestCase(TestRIB)
    return [suiteRIB]

if __name__ == '__main__':
    unittest.main()
