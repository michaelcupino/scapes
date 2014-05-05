#!/usr/bin/python

import main
import unittest
import webapp2
import webtest

from google.appengine.ext import testbed

class MainTest(unittest.TestCase):

  def setUp(self):
    app = main.app
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
  
  def testDocumentAnalysis(self):  
    # TODO(michaelcupino): Mock out handlers and only assert that the get method
    # of the handler was called. Do not assert the response of the body.
    response = self.testapp.get('/document-analysis')
    self.assertEqual('Start the DocumentAnalysisPipeline', response.body)

if __name__ == '__main__':
  unittest.main()

