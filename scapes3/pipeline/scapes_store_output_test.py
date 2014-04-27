#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.scapes_store_output import ScapesStoreOutput

class ScapesStoreOutputTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testRun(self):
    # TODO(michaelcupino): Find out how to test pipeline
    self.assertEqual(1, 1 + 0)

if __name__ == '__main__':
  unittest.main()

