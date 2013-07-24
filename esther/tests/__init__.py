import unittest


def build_suite(labels):
    suite = None

    if labels:
        suite = unittest.defaultTestLoader.loadTestsFromNames(labels)
        if not suite.countTestCases():
            suite = None

    if suite is None:
        return unittest.defaultTestLoader.discover('.')

    return suite


def run_tests(verbosity=1, labels=None):
    suite = build_suite(labels)
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return result.wasSuccessful()
