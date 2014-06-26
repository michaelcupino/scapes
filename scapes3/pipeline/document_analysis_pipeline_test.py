#!/usr/bin/python

import os
import unittest
import urllib2

from StringIO import StringIO
from apiclient.http import HttpMockSequence
from google.appengine.ext import testbed
from mock import MagicMock
from mock import patch
from oauth2client.client import OAuth2Credentials
from pipeline.document_analysis_pipeline import DocumentAnalysisPipeline
from pipeline.revision_fetcher_pipeline import RevisionFetcherPipeline

# TODO(michaelcupino): Move this to a test_utils package.
def datafile(filename):
  return os.path.join(os.path.dirname(__file__), filename)


class DocumentAnalysisPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()

  @patch.object(urllib2, 'urlopen')
  @patch.object(OAuth2Credentials, 'from_json')
  def testRun(self, mockOAuth2CredentialsFromJsonMethod, mockUrlOpenMethod):
    http = HttpMockSequence([
      ({'status': '200'}, open(datafile('test-drive-revisions-list-0.json'),
          'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials
    exportLinks = [
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=697&exportFormat=tx'
          't'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=698&exportFormat=tx'
          't'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=868&exportFormat=tx'
          't'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=869&exportFormat=tx'
          't'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=937&exportFormat=tx'
          't'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=939&exportFormat=tx'
          't'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=1035&exportFormat=t'
          'xt'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=1036&exportFormat=t'
          'xt'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=1048&exportFormat=t'
          'xt'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=1049&exportFormat=t'
          'xt'),
      ('https://docs.google.com/feeds/download/documents/export/Export?id=1Duz2'
          'yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=1057&exportFormat=t'
          'xt')
    ]
    exportedText = {
      exportLinks[0]: StringIO('Hello'),
      exportLinks[1]: StringIO('Hello world.'),
      exportLinks[2]: StringIO('Hello'),
      exportLinks[3]: StringIO(''),
      exportLinks[4]: StringIO('Hello again, this is a longer sentence'),
      exportLinks[5]: StringIO(('Hello again, this is a longer sentence with '
          'another word')),
      exportLinks[6]: StringIO(('Hello again, this is a longer sentence with '
          'another word. Here is another sentence')),
      exportLinks[7]: StringIO(('Hello again, this is a longer sentence with '
          'another word. Here is another sentence with another word')),
      exportLinks[8]: StringIO(('Hello again, this is a longer sentence with '
          'another word. Here is another sentence with another word')),
      exportLinks[9]: StringIO(('Hello again, this is a longer sentence with '
          'another word. Here is another sentence.')),
      exportLinks[10]: StringIO(('Hello again, this is a longer sentence with '
          'another word. Here is another sentence. The end.'))
    }
    mockUrlOpenMethod.side_effect = lambda url: exportedText[url]

    pipeline = DocumentAnalysisPipeline('test@example.com', 'abc123', None)
    pipeline.start_test()
    result = pipeline.outputs.default.value
    self.assertEqual([5, 7, -7, -5, 38, 18, 26, 18, 0, -17, 9], result)

if __name__ == '__main__':
  unittest.main()

