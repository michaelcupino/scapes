#!/usr/bin/python

import os
import unittest

from apiclient.http import HttpMockSequence
from google.appengine.ext import testbed
from mock import MagicMock
from mock import patch
from oauth2client.client import OAuth2Credentials
from pipeline.document_revisions_pipeline import DocumentRevisionsPipeline

# TODO(michaelcupino): Move this to a test_utils package.
def datafile(filename):
  return os.path.join(os.path.dirname(__file__), filename)


# TODO(michaelcupino): Create a test_matchers module inside the test_utils
# package and move this to that module.
class StringContainsMatcher:
  """Matcher class that matches if the expectedString is contained in the
  actual string
  """

  def __init__(self, expectedString, expectedLines):
    """Creates an instance of StringContainsMatcher

    Args:
      expectedString: string, The string that is expected to be contained in the
        actual compared string.
      expectedLines: int, The number of lines expected in the actual compared
        string.
    """
    self.expectedString = expectedString
    self.expectedLines = expectedLines
  
  def __eq__(self, actualString):
    return (self.expectedString in actualString and
        len(actualString.splitlines()) is self.expectedLines)


class DocumentRevisionsPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  @patch.object(OAuth2Credentials, 'from_json')
  def testRun(self, mockOAuth2CredentialsFromJsonMethod):
    # TODO(michaelcupino): Move test json files into a test_utils package.
    http = HttpMockSequence([
      ({'status': '200'}, open(datafile('test-drive-revisions-list-0.json'),
          'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials

    pipeline = DocumentRevisionsPipeline('test@example.com', 'abc123', None)
    pipeline.start_test()
    result = pipeline.outputs.default.value

    self.assertIn(('https://docs.google.com/feeds/download/documents/export/Exp'
        'ort?id=1Duz2yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=697&expor'
        'tFormat=txt'), result[0]['exportLink'])
    self.assertIn(('https://docs.google.com/feeds/download/documents/export/Exp'
        'ort?id=1Duz2yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=698&expor'
        'tFormat=txt'), result[1]['exportLink'])


if __name__ == '__main__':
  unittest.main()

