"""
Simple module defining unittest testcases for project doctests
"""
import doctest

import user, auth

def load_tests(loader, tests, ignore):
    """
    add doctests for this package
    """
    tests.addTests(doctest.DocTestSuite(auth))
    tests.addTests(doctest.DocTestSuite(user))
    return tests
