#!/usr/bin/python

import unittest
import webapp2
import webtest

from google.appengine.ext import testbed
from handler.revisions_analysis_handler import RevisionsAnalysisHandler

class RevisionsAnalysisHandlerTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication(
        [('/revisions-analysis', RevisionsAnalysisHandler)],
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
  
  def testGet(self):
    response = self.testapp.get('/revisions-analysis')
    self.assertEqual('Start the RevisionsAnalysisPipeline', response.body)

if __name__ == '__main__':
  unittest.main()

