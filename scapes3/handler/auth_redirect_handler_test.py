#!/usr/bin/python

import unittest
import webapp2
import webtest

from google.appengine.ext import testbed
from handler.auth_redirect_handler import AuthRedirectHandler
from mock import patch
from service import config

class AuthRedirectHandlerTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication(
        [('/authredirect', AuthRedirectHandler)],
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
    response = self.testapp.get('/authredirect')

    self.assertEquals(302, response.status_code)
    self.assertIn('https://accounts.google.com/o/oauth2/auth?state=',
        response.location)

  @patch.object(config.decorator, 'has_credentials')
  def testGet_unauth(self, mockHasCredentialsMethod):
    mockHasCredentialsMethod.return_value = True

    response = self.testapp.get('/authredirect')

    self.assertEquals(302, response.status_code)
    self.assertEquals('http://localhost/', response.location)

if __name__ == '__main__':
  unittest.main()

