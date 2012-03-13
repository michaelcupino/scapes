import unittest
import main

# http://docs.python.org/library/test.html#writing-tests
# http://code.google.com/p/gaeunit/wiki/Readme
# http://code.google.com/appengine/docs/python/tools/localunittesting.html#Writing_Datastore_and_Memcache_Tests

class MainTest(unittest.TestCase):

  def setUp(self):
    y = 0

  def tearDown(self):
    y = None

  def testFunction1(self):
    x = 0
    self.assertEqual(0, x)
    self.assertTrue(True)

  def testAwesomeness2(self):
    x = 0
    self.assertEqual(0, x)
    self.assertTrue(True)
