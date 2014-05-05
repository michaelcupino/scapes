#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.document_analysis_pipeline import DocumentAnalysisPipeline

class DocumentAnalysisPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()

  def tearDown(self):
    self.testbed.deactivate()

  def testRun(self):
    self.assertEqual(1, 0 + 1)

if __name__ == '__main__':
  unittest.main()
