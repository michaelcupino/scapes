#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.folder_analysis_pipeline import FolderAnalysisPipeline

class FolderAnalysisPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()

  def tearDown(self):
    self.testbed.deactivate()

  # TODO(michaelcupino): Test that an email is sent after there is an analyses.
  def testRun(self):
    self.assertEqual(1, 0 + 1)

if __name__ == '__main__':
  unittest.main()

