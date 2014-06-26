#!/usr/bin/python

import unittest
import urllib2

from StringIO import StringIO
from google.appengine.ext import testbed
from mock import MagicMock
from mock import patch
from pipeline.revisions_analysis_pipeline import RevisionsAnalysisPipeline

class RevisionsAnalysisPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()

  @patch.object(urllib2, 'urlopen')
  def testRun(self, mockUrlOpenMethod):
    exportLinks = [
      'docs.google.com/123',
      'docs.google.com/456',
      'docs.google.com/789'
    ]
    exportedText = {
      exportLinks[0]: StringIO('Hello'),
      exportLinks[1]: StringIO('Hello world.'),
      exportLinks[2]: StringIO('Hello.'),
    }
    mockUrlOpenMethod.side_effect = lambda url: exportedText[url]

    pipeline = RevisionsAnalysisPipeline(exportLinks)
    pipeline.start_test()
    result = pipeline.outputs.default.value
    self.assertEqual([5, 7, -6], result)

if __name__ == '__main__':
  unittest.main()

