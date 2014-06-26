#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.revision_fetcher_pipeline import RevisionFetcherPipeline

class RevisionFetcherPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testRun(self):
    pipeline = RevisionFetcherPipeline('http://www.google.com/robots.txt')
    pipeline.start_test()
    result = pipeline.outputs.default.value
    self.assertIn('Disallow: /images', result)


if __name__ == '__main__':
  unittest.main()

