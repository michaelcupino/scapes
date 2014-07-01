#!/usr/bin/python

import unittest
import webapp2
import webtest

from google.appengine.ext import testbed
from handler.document_analysis_handler import DocumentAnalysisHandler
from mock import MagicMock
from mock import PropertyMock
from mock import patch
from pipeline.document_analysis_pipeline import DocumentAnalysisPipeline
from service import config


# TODO(michaelcupino): Create a test_matchers module inside the test_utils
# package and move this to that module.
class AnyMatcher:
  """Matcher class that matches to anything."""

  def __init__(self):
    pass

  def __eq__(self, a):
    return True


class DocumentAnalysisHandlerTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication(
        [('/document-analysis', DocumentAnalysisHandler)],
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
    response = self.testapp.post_json('/document-analysis', {'docId': 'abc'})
    self.assertIn('"statusMessage": "SCAPES is not authorized to access your ',
        response.body)
    self.assertIn('"authUrl": "/authredirect"', response.body)

  @patch('handler.document_analysis_handler.DocumentAnalysisPipeline')
  @patch.object(config.decorator, 'get_credentials')
  @patch.object(config.decorator, 'has_credentials')
  def testGet_auth(self, mockHasCredentialsMethod, mockGetCredentialsMethod,
      mockDocumentAnalysisPipeline):
    mockHasCredentialsMethod.return_value = True
    mockCredentialsAsJsonMethod = MagicMock(return_value={})
    mockGetCredentialsMethod.to_json = mockCredentialsAsJsonMethod
    mockDocumentAnalysisPipeline.return_value.base_path = 'test-base'
    mockDocumentAnalysisPipeline.return_value.pipeline_id = 'pipeline123'

    response = self.testapp.post_json('/document-analysis',
        {'docId': 'doc123abc'})

    mockDocumentAnalysisPipeline.assert_called_with('test@example.com',
        'doc123abc', AnyMatcher())
    self.assertIn(('"statusMessage": "Document analysis has started. List '
        'of character diffs will'), response.body)
    self.assertIn('"pipelineUrl": "test-base/status?root=pipeline123"',
        response.body)

if __name__ == '__main__':
  unittest.main()

