#!/usr/bin/python

import os
import unittest

from apiclient.http import HttpMockSequence
from google.appengine.ext import testbed
from mock import MagicMock
from mock import patch
from oauth2client.client import OAuth2Credentials
from pipeline.document_revisions_pipeline import DocumentRevisionsPipeline
from pipeline.email_pipeline import EmailPipeline

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
    self.testbed.init_mail_stub()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_taskqueue_stub()

  def tearDown(self):
    self.testbed.deactivate()

  @patch.object(EmailPipeline, 'start')
  @patch.object(EmailPipeline, '__init__')
  @patch.object(OAuth2Credentials, 'from_json')
  def testRun(self, mockOAuth2CredentialsFromJsonMethod,
      mockEmailPipelineConstructor,
      mockEmailPipelineStartMethod):
    # TODO(michaelcupino): Move test json files into a test_utils package.
    http = HttpMockSequence([
      ({'status': '200'}, open(datafile('test-drive-revisions-list-0.json'),
          'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials
    mockEmailPipelineConstructor.return_value = None

    pipeline = DocumentRevisionsPipeline()
    pipeline.run('test@example.com', 'abc123', None)

    expectedSubsetBody = ('[\n'
        '  "https://docs.google.com/feeds/download/documents/export/Export?id=1'
        'Duz2yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=697&exportFormat='
        'txt", \n'
        '  "https://docs.google.com/feeds/download/documents/export/Export?id=1'
        'Duz2yYSTSgdWQhTgEJ3zPELKTHS3WGhPVLQk1PDJm3Q&revision=698&exportFormat='
        'txt", \n')
    mockEmailPipelineConstructor.assert_called_with('test@example.com',
        'SCAPES Robot: Revision export links from document abc123',
        StringContainsMatcher(expectedSubsetBody, expectedLines=13))
    mockEmailPipelineStartMethod.assert_called_with()


if __name__ == '__main__':
  unittest.main()

