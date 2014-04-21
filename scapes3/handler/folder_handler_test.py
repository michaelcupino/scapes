#!/usr/bin/python
import unittest
import webapp2
import webtest

from handler.folder_handler import Folder
from google.appengine.ext import testbed
from google.appengine.api import users
from model.file_model import File

class FolderHandlerTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication([('/folder', Folder)], debug=True)
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

  def testPost(self):
    params = {
        'folder_name': 'folder name',
        'file_content': 'id1, id2, id3, id4, id5',
    }
    response = self.testapp.post('/folder', params)
    self.assertEqual(response.status_int, 200)

  def testPutsFileWithCorrectAuthor(self):
    params = {
        'folder_name': 'folder name',
        'file_content': 'id1, id2, id3, id4, id5',
    }
    response = self.testapp.post('/folder', params)

    queryResults = File.query().fetch(2)
    actualFile = queryResults[0]

    self.assertEqual('test@example.com', actualFile.author.email())

if __name__ == '__main__':
  unittest.main()

