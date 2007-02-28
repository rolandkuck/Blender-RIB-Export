import unittest

import test_parse
import test_rib

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(test_parse.retrieveTestSuite())
    suite.addTests(test_rib.retrieveTestSuite())
    unittest.TextTestRunner().run(suite)
