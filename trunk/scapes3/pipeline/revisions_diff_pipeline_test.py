#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.revisions_diff_pipeline import RevisionsDiffPipeline

class RevisionsDiffPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testRun(self):
    pipeline = RevisionsDiffPipeline('Hello', 'Hello there')
    pipeline.start_test()
    result = pipeline.outputs.default.value

    self.assertEqual(result, 6)

if __name__ == '__main__':
  unittest.main()

