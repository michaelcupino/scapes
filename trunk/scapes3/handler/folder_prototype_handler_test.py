#!/usr/bin/python
import unittest
import os
import webapp2
import webtest

from apiclient.http import HttpMockSequence
from google.appengine.ext import testbed
from google.appengine.api import users
from handler.folder_prototype_handler import FolderPrototypeHandler
from model.file_model import ScapesFile
from mock import MagicMock
from mock import patch

def datafile(filename):
  return os.path.join(os.path.dirname(__file__), filename)

class FolderPrototypeHandlerTest(unittest.TestCase):

  def setUp(self):
    
    app = webapp2.WSGIApplication([(r'/folder/(.*)', FolderPrototypeHandler)],
        debug=True)
    self.testapp = webtest.TestApp(app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.setup_env(
        USER_EMAIL = 'test@example.com',
        USER_ID = '123',
        USER_IS_ADMIN = '0',
        overwrite = True)

  def tearDown(self):
    self.testbed.deactivate()

  def testGet_unauthorized(self):
    response = self.testapp.get('/folder/123')
    self.assertIn('https://accounts.google.com/o/oauth2/auth', response.body,
        ('Should ask the user to authorize SCAPES to access his or her Google'
        'Drive data by showing them the authorize url.'))

  @patch('service.config.decorator')
  def testGet_noNextPageToken(self, MockOauth2Decorator):
    books_discovery = {}
    http = HttpMockSequence([
      ({'status': '200'}, open(datafile('test-drive-children-list-4.json'), 'rb').read()),
    ])
    MockOauth2Decorator.has_credentials = MagicMock(return_value=True)
    MockOauth2Decorator.http = MagicMock(return_value=http)

    response = self.testapp.get('/folder/123')

    self.assertIn('<pre>1 documents</pre>', response.body)

  @patch('service.config.decorator')
  def testGet_withNextPageToken(self, MockOauth2Decorator):
    books_discovery = {}
    http = HttpMockSequence([
      ({'status': '200'}, open(datafile('test-drive-children-list-0.json'), 'rb').read()),
      ({'status': '200'}, open(datafile('test-drive-children-list-1.json'), 'rb').read()),
      ({'status': '200'}, open(datafile('test-drive-children-list-2.json'), 'rb').read()),
      ({'status': '200'}, open(datafile('test-drive-children-list-3.json'), 'rb').read()),
    ])
    MockOauth2Decorator.has_credentials = MagicMock(return_value=True)
    MockOauth2Decorator.http = MagicMock(return_value=http)

    response = self.testapp.get('/folder/123')

    self.assertIn('<pre>343 documents</pre>', response.body)

if __name__ == '__main__':
  unittest.main()

