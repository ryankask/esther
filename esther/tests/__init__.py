import unittest

def suite():
    suite = unittest.defaultTestLoader.discover('.')
    return suite

def run_tests(verbosity=1):
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite())
    return result.wasSuccessful()
