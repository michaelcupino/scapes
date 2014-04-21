#!/usr/bin/python

import unittest
import webapp2
import webtest

from google.appengine.ext import testbed
from handler.index_handler import IndexHandler

class IndexHandlerTest(unittest.TestCase):

  def setUp(self):

    app = webapp2.WSGIApplication([('/', IndexHandler)], debug=True)
    self.testapp = webtest.TestApp(app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_blobstore_stub()
    self.testbed.setup_env(
        USER_EMAIL = 'test@example.com',
        USER_ID = '123',
        USER_IS_ADMIN = '0',
        overwrite = True)

  def tearDown(self):
    self.testbed.deactivate()

  def testGet(self):
    # TODO(michaelcupino): Find out if FileMetadata entry is used by scapes.
    response = self.testapp.get('/')
    self.assertEqual(response.status_int, 200)

  def testPostShouldRedirect(self):
    params = {
        'scapes_folder_id': '123'
    }
    response = self.testapp.post('/', params)
    self.assertEqual(response.status_int, 302)
    # TODO(michaelcupnio): Assert that the pipeline has been started.

if __name__ == '__main__':
  unittest.main()

