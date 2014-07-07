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

  # TODO(michaelcupino): Add a test that tests failure case.
  def testRun(self):
    pass


if __name__ == '__main__':
  unittest.main()

