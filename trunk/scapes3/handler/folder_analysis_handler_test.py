#!/usr/bin/python

import unittest
import webapp2
import webtest

from google.appengine.ext import testbed
from mock import MagicMock
from pipeline.folder_analysis_pipeline import FolderAnalysisPipeline
from handler.folder_analysis_handler import FolderAnalysisHandler
from mock import patch
from service import config

# TODO(michaelcupino): Create a test_matchers module inside the test_utils
# package and move this to that module.
class AnyMatcher:
  """Matcher class that matches to anything."""

  def __init__(self):
    pass

  def __eq__(self, a):
    return True

class FolderAnalysisHandlerTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication(
        [('/folder-analysis', FolderAnalysisHandler)],
        debug=True)
    self.testapp = webtest.TestApp(app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_memcache_stub()
    self.testbed.init_datastore_v3_stub()
    self.testbed.setup_env(
        USER_EMAIL = 'test@example.com',
        USER_ID = '123',
        USER_IS_ADMIN = '0',
        overwrite = True)

  def tearDown(self):
    self.testbed.deactivate()
  
  def testGet_unauth(self):
    response = self.testapp.post_json('/folder-analysis', {'folderId': 'abc'})
    self.assertIn('"statusMessage": "SCAPES is not authorized to access your ',
        response.body)
    self.assertIn('"authUrl": "/authredirect"', response.body)

  @patch('handler.folder_analysis_handler.FolderAnalysisPipeline')
  @patch.object(config.decorator, 'get_credentials')
  @patch.object(config.decorator, 'has_credentials')
  def testGet_auth(self, mockHasCredentialsMethod, mockGetCredentialsMethod,
      mockFolderAnalysisPipeline):
    mockHasCredentialsMethod.return_value = True
    mockCredentialsAsJsonMethod = MagicMock(return_value={})
    mockGetCredentialsMethod.to_json = mockCredentialsAsJsonMethod
    mockFolderAnalysisPipeline.return_value.base_path = 'test-base'
    mockFolderAnalysisPipeline.return_value.pipeline_id = 'pipeline123'

    response = self.testapp.post_json('/folder-analysis',
        {'folderId': 'folder123abc'})

    mockFolderAnalysisPipeline.assert_called_with('test@example.com',
        'folder123abc', AnyMatcher())
    self.assertIn(('"statusMessage": "Folder analysis has started. List '
        'of character diffs will'), response.body)
    self.assertIn('"pipelineUrl": "test-base/status?root=pipeline123"',
        response.body)

if __name__ == '__main__':
  unittest.main()

