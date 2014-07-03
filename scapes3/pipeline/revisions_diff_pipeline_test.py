#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.revisions_diff_pipeline import RevisionsDiffPipeline
from model.revision import Revision

class RevisionsDiffPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testRun(self):
    pipeline = RevisionsDiffPipeline('Hello', 'Hello there', {})
    pipeline.start_test()
    result = pipeline.outputs.default.value

    expected = Revision()
    expected.wordsAdded = 1
    expected.wordsDeleted = 0
    expected.wordCount= 2
    self.assertEqual(result, expected.to_dict())

  # TODO(michaelcupino): Test isRemove, isAdd, etc.

if __name__ == '__main__':
  unittest.main()

