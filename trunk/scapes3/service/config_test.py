#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from service import config

class IndexHandlerTest(unittest.TestCase):

  def setUp(self):
    reload(config)
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testServiceIsNone(self):
    self.assertEqual(None, config.service)

  def testServiceIsAssigned(self):
    expected = config.getService()
    self.assertEqual(expected, config.service)


if __name__ == '__main__':
  unittest.main()

