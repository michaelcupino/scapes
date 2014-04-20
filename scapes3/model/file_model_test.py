#!/usr/bin/python
import unittest

from google.appengine.ext import testbed
from google.appengine.api import users

from file_model import File

class FileModelTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testSomething(self):
    self.assertEqual(1, 1 + 0)

  def testPut(self):
    testFile = File()
    testFile.author = users.get_current_user()
    testFile.put()
    # TODO(michaelcupino): Assert that the author that was stored is the same
    # as the current user.
    self.assertEqual(2, 1 + 1)

if __name__ == '__main__':
  unittest.main()
