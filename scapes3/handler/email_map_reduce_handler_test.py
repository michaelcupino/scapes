#!/usr/bin/python

import unittest
import webapp2
import webtest

from google.appengine.ext import testbed
from handler.email_map_reduce_handler import EmailMapReduceHandler
from mock import MagicMock
from mock import patch
from pipeline.email_pipeline import EmailPipeline

class MailMapReduceHandlerTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication([('/emailmr', EmailMapReduceHandler)],
        debug=True)
    self.testapp = webtest.TestApp(app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.setup_env(
        USER_EMAIL = 'test@example.com',
        USER_ID = '123',
        USER_IS_ADMIN = '0',
        overwrite = True)

  def tearDown(self):
    self.testbed.deactivate()
  
  @patch.object(EmailPipeline, 'start')
  @patch.object(EmailPipeline, '__init__')
  def testGet(self, mockEmailPipelineConstructor, mockEmailPipelineStartMethod):
    mockEmailPipelineConstructor.return_value = None

    response = self.testapp.get('/emailmr')

    mockEmailPipelineConstructor.assert_called_with('test@example.com')
    mockEmailPipelineStartMethod.assert_called_with()
    self.assertEqual(('Map reduce job has been started. Email will be sent '
        'soon.'), response.body)

if __name__ == '__main__':
  unittest.main()

