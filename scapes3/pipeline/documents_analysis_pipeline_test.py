#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.documents_analysis_pipeline import DocumentsAnalysisPipeline

class DocumentsAnalysisPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()

  def tearDown(self):
    self.testbed.deactivate()

  # TODO(michaelcupino): Test that the DocumentAnalysisPipeline gets called for
  # each document.
  def testRun(self):
    self.assertEqual(1, 0 + 1)

if __name__ == '__main__':
  unittest.main()

