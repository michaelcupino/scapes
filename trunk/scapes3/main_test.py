#!/usr/bin/python

import main
import unittest
import webtest

from google.appengine.ext import testbed

class MainTest(unittest.TestCase):

  def setUp(self):
    app = main.app
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
  
  def testDocumentAnalysis(self):  
    # TODO(michaelcupino): Figure out why webtest doesn't like it when a post
    # method is mocked. I think the key is to get something like Jasmine's spy
    # "andCallThrough" method.
    response = self.testapp.post('/document-analysis')

if __name__ == '__main__':
  unittest.main()

