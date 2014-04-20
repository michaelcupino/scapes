#!/usr/bin/python
import unittest

from google.appengine.ext import testbed

class FileModelTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()

  def tearDown(self):
    self.testbed.deactivate()

  def testSomething(self):
    self.assertEqual(1, 1 + 0)

if __name__ == '__main__':
  unittest.main()
