#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from service import utils

class UtilsTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testSplitIntoSentences(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testSplitIntoWords(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testscapesWriteToBlobstore(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testScapesAnalyseDocument(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testScapesAnalyzeReduce(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testScapesAnalyzeRevision(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

if __name__ == '__main__':
  unittest.main()

