#!/usr/bin/python
import unittest

from datetime import datetime
from file_model import File
from google.appengine.ext import testbed
from google.appengine.api import users

class FileModelTest(unittest.TestCase):

  def setUp(self):
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

  def testQueryLength(self):
    testFile = File()
    testFile.put()

    queryResults = File.query().fetch(2)
    self.assertEqual(1, len(queryResults))
  
  def testAuthor(self):
    testFile = File()
    testFile.author = users.get_current_user()
    testFile.put()

    queryResults = File.query().fetch(2)
    actualFile = queryResults[0]

    self.assertEqual('test@example.com', actualFile.author.email())

  def testListOfId(self):
    testFile = File()
    testFile.list_of_id = 'id1, id2, id3, id4, id5'
    testFile.put()

    queryResults = File.query().fetch(2)
    actualFile = queryResults[0]

    self.assertEqual('id1, id2, id3, id4, id5', actualFile.list_of_id)

  def testDate(self):
    testFile = File()
    testFile.date = datetime(2014, 4, 20)
    testFile.put()

    queryResults = File.query().fetch(2)
    actualFile = queryResults[0]

    self.assertEqual(datetime(2014, 4, 20), actualFile.date)

if __name__ == '__main__':
  unittest.main()
