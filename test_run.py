import unittest

import test_parse

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(test_parse.retrieveTestSuite())
    unittest.TextTestRunner().run(suite)
