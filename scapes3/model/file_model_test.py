#!/usr/bin/python
import unittest

from datetime import datetime
from google.appengine.ext import testbed
from google.appengine.api import users
from model.file_model import ScapesFile

class ScapesFileModelTest(unittest.TestCase):

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
    testScapesFile = ScapesFile()
    testScapesFile.put()

    queryResults = ScapesFile.query().fetch(2)
    self.assertEqual(1, len(queryResults))
  
  def testAuthor(self):
    testScapesFile = ScapesFile()
    testScapesFile.author = users.get_current_user()
    testScapesFile.put()

    queryResults = ScapesFile.query().fetch(2)
    actualScapesFile = queryResults[0]

    self.assertEqual('test@example.com', actualScapesFile.author.email())

  def testListOfId(self):
    testScapesFile = ScapesFile()
    testScapesFile.list_of_id = 'id1, id2, id3, id4, id5'
    testScapesFile.put()

    queryResults = ScapesFile.query().fetch(2)
    actualScapesFile = queryResults[0]

    self.assertEqual('id1, id2, id3, id4, id5', actualScapesFile.list_of_id)

  def testDate(self):
    testScapesFile = ScapesFile()
    testScapesFile.date = datetime(2014, 4, 20)
    testScapesFile.put()

    queryResults = ScapesFile.query().fetch(2)
    actualScapesFile = queryResults[0]

    self.assertEqual(datetime(2014, 4, 20), actualScapesFile.date)

if __name__ == '__main__':
  unittest.main()

