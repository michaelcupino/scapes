#!/usr/bin/python

import unittest
import webapp2
import webtest

from google.appengine.ext import testbed
from handler.document_revisions_mr_handler import DocumentRevisionsMRHandler
from mock import MagicMock
from mock import patch
from oauth2client.client import OAuth2Credentials
from pipeline.document_revisions_pipeline import DocumentRevisionsPipeline

class DocumentRevisionsMRHandlerTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication(
        [(r'/documentmr/(.*)/revisions', DocumentRevisionsMRHandler)],
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
  
  def testGet_unauthorized(self):
    response = self.testapp.get('/documentmr/abc123/revisions')
    self.assertIn('https://accounts.google.com/o/oauth2/auth', response.body,
        ('Should ask the user to authorize SCAPES to access his or her Google'
        'Drive data by showing them the authorize url.'))

  @patch('service.config.decorator')
  @patch.object(DocumentRevisionsPipeline, 'start')
  @patch.object(DocumentRevisionsPipeline, '__init__')
  def testGet_authorized(self, mockDocumentRevisionsPipelineConstructor,
      mockDocumentRevisionsPipelineStartMethod,
      MockOauth2Decorator):
    mockDocumentRevisionsPipelineConstructor.return_value = None
    MockOauth2Decorator.has_credentials = MagicMock(return_value=True)

    response = self.testapp.get('/documentmr/abc123/revisions')

    mockDocumentRevisionsPipelineConstructor.assert_called_with(
        'test@example.com', 'abc123',
        MockOauth2Decorator.get_credentials().to_json())
    mockDocumentRevisionsPipelineStartMethod.assert_called_with()
    self.assertEqual(('Map reduce job has been started. List of revisions '
        'will sent to test@example.com.'), response.body)

if __name__ == '__main__':
  unittest.main()

