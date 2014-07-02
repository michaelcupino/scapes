#!/usr/bin/python

import os
import unittest

from apiclient.http import HttpMockSequence
from google.appengine.ext import testbed
from mock import MagicMock
from mock import patch
from oauth2client.client import OAuth2Credentials
from pipeline.folder_fetcher_pipeline import FolderFetcherPipeline

# TODO(michaelcupino): Move this to a test_utils package.
def datafile(filename):
  return os.path.join(os.path.dirname(__file__), filename)

class FolderFetcherPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()

  @patch.object(OAuth2Credentials, 'from_json')
  def testRun_emptyFolder(self, mockOAuth2CredentialsFromJsonMethod):
    # TODO(michaelcupino): Move test json files into a test_utils package.
    http = HttpMockSequence([
      ({'status': '200'}, open(datafile('test-drive-children-list-empty.json'),
          'rb').read()),
      ({'status': '200'}, open(datafile('test-drive-children-list-empty.json'),
          'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials

    pipeline = FolderFetcherPipeline('/folder123', None)
    pipeline.start_test()
    result = pipeline.outputs.default.value

    self.assertEqual([], result)

  @patch.object(OAuth2Credentials, 'from_json')
  def testRun_folderWithOneDoc(self, mockOAuth2CredentialsFromJsonMethod):
    # TODO(michaelcupino): Move test json files into a test_utils package.
    http = HttpMockSequence([
      # Recursion level 0: Has 0 folders
      ({'status': '200'}, open(datafile('test-drive-children-list-empty.json'),
          'rb').read()),
      # Recursion level 0: Has 0 documents
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-a.json'), 'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials

    pipeline = FolderFetcherPipeline('/folder123', None)
    pipeline.start_test()
    result = pipeline.outputs.default.value

    self.assertEqual(['1vN98-jz7tx_mal-p_gn-vbQLH7Yq1-yi7Lc7Zw8Uy60'], result)

  @patch.object(OAuth2Credentials, 'from_json')
  def testRun_folderWithOneDocAndFolder(self,
      mockOAuth2CredentialsFromJsonMethod):
    # TODO(michaelcupino): Move test json files into a test_utils package.
    http = HttpMockSequence([
      # Recursion level 0: Has 1 folder
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-a.json'), 'rb').read()),
      # Recursion level 1: Has 0 folders
      ({'status': '200'}, open(datafile('test-drive-children-list-empty.json'),
          'rb').read()),
      # Recursion level 1: Has 1 document (1vN98...)
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-a.json'), 'rb').read()),
      # Recursion level 0: Has 1 document (abc123)
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-b.json'), 'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials

    pipeline = FolderFetcherPipeline('/folder123', None)
    pipeline.start_test()
    result = pipeline.outputs.default.value

    self.assertEqual(['abc123', '1vN98-jz7tx_mal-p_gn-vbQLH7Yq1-yi7Lc7Zw8Uy60'],
        result)

  @patch.object(OAuth2Credentials, 'from_json')
  def testRun_folderPageToken(self,
      mockOAuth2CredentialsFromJsonMethod):
    # TODO(michaelcupino): Move test json files into a test_utils package.
    http = HttpMockSequence([
      # Recursion level 0: Has 1 folder and a page token
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-page.json'), 'rb').read()),
      # Recursion level 1: Has 0 folders
      ({'status': '200'}, open(datafile('test-drive-children-list-empty.json'),
          'rb').read()),
      # Recursion level 1: Has 1 document (1vN98...)
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-a.json'), 'rb').read()),
      # Recursion level 0: Has 1 folder and no page token
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-b.json'), 'rb').read()),
      # Recursion level 1: Has 0 folders
      ({'status': '200'}, open(datafile('test-drive-children-list-empty.json'),
          'rb').read()),
      # Recursion level 1: Has 1 document (abc123)
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-b.json'), 'rb').read()),
      # Recursion level 0: Has 1 document (def456)
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-c.json'), 'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials

    pipeline = FolderFetcherPipeline('/folder123', None)
    pipeline.start_test()
    result = pipeline.outputs.default.value

    expected = [
      'def456',
      '1vN98-jz7tx_mal-p_gn-vbQLH7Yq1-yi7Lc7Zw8Uy60',
      'abc123',
    ]
    self.assertEqual(expected, result)

  @patch.object(OAuth2Credentials, 'from_json')
  def testRun_docPageToken(self,
      mockOAuth2CredentialsFromJsonMethod):
    # TODO(michaelcupino): Move test json files into a test_utils package.
    http = HttpMockSequence([
      # Recursion level 0: Has 0 folders
      ({'status': '200'}, open(datafile('test-drive-children-list-empty.json'),
          'rb').read()),
      # Recursion level 0: Has 1 document (1o0L3...) with a page token
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-page.json'), 'rb').read()),
      # Recursion level 0: Has 1 document (1vN98...) with no page token
      ({'status': '200'}, open(datafile(
          'test-drive-children-list-1-item-a.json'), 'rb').read()),
    ])
    mockCredentials = MagicMock(name='mockCredentials')
    mockCredentials.authorize = MagicMock(return_value=http)
    mockOAuth2CredentialsFromJsonMethod.return_value = mockCredentials

    pipeline = FolderFetcherPipeline('/folder123', None)
    pipeline.start_test()
    result = pipeline.outputs.default.value

    expected = [
      '1o0L3UOiubzeBZNFEyKzZrUfVdWZ4K4-WeINn83VkwAI',
      '1vN98-jz7tx_mal-p_gn-vbQLH7Yq1-yi7Lc7Zw8Uy60',
    ]
    self.assertEqual(expected, result)

if __name__ == '__main__':
  unittest.main()

