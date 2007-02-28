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
