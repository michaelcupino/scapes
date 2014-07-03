#!/usr/bin/python

import unittest
import urllib2

from StringIO import StringIO
from google.appengine.ext import testbed
from mock import MagicMock
from mock import patch
from pipeline.revisions_analysis_pipeline import RevisionsAnalysisPipeline
from model.revision import Revision

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

    revision1 = Revision()
    revision1.wordsAdded = 25
    revision1.wordsDeleted = 5
    revision2 = Revision()
    revision2.wordsAdded = 25
    revision2.wordsDeleted = 7
    revision3 = Revision()
    revision3.wordsAdded = 25
    revision3.wordsDeleted = -6
    self.assertEqual([revision1.to_dict(), revision2.to_dict(),
        revision3.to_dict()], result)

if __name__ == '__main__':
  unittest.main()

