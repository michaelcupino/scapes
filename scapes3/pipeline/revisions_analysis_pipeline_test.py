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
    mockRevisions = [
      Revision(exportLink=exportLinks[0]).to_dict(),
      Revision(exportLink=exportLinks[1]).to_dict(),
      Revision(exportLink=exportLinks[2]).to_dict()
    ]
    exportedText = {
      exportLinks[0]: StringIO('Hello'),
      exportLinks[1]: StringIO('Hello world.'),
      exportLinks[2]: StringIO('Hello.'),
    }
    mockUrlOpenMethod.side_effect = lambda url: exportedText[url]

    # TODO(michaelcupino): Fix tests
    pipeline = RevisionsAnalysisPipeline(mockRevisions, None)
    pipeline.start_test()
    result = pipeline.outputs.default.value

    revision1 = Revision()
    revision1.wordsAdded = 1
    revision1.wordsDeleted = 0
    revision1.wordCount = 1
    revision1.exportLink = 'docs.google.com/123'
    revision2 = Revision()
    revision2.wordsAdded = 1
    revision2.wordsDeleted = 0
    revision2.wordCount = 2
    revision2.exportLink = 'docs.google.com/456'
    revision3 = Revision()
    revision3.wordsAdded = 0
    revision3.wordsDeleted = 1
    revision3.wordCount = 1
    revision3.exportLink = 'docs.google.com/789'
    self.assertEqual([revision1.to_dict(), revision2.to_dict(),
        revision3.to_dict()], result)

if __name__ == '__main__':
  unittest.main()

