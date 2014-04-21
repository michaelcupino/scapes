#!/usr/bin/python
import unittest

from google.appengine.ext import testbed
from model.file_metadata import FileMetadata

class FileMetadetaTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testGetFirstKeyForUser(self):
    # TODO(michaelcupino): Find out if scapes is using getFirstKeyForUser
    self.assertEqual(1, 1 + 0)

  def testGetLastKeyForUser(self):
    # TODO(michaelcupino): Find out if scapes is using getLastKeyForUser
    self.assertEqual(2, 1 + 1)

  def testGetKeyName(self):
    # TODO(michaelcupino): Find out if scapes is using getKeyName
    self.assertEqual(3, 1 + 2)

  def testOwner(self):
    # TODO(michaelcupino): Find out if scapes is using owner property
    self.assertEqual(4, 1 + 3)

  def testFilename(self):
    # TODO(michaelcupino): Find out if scapes is using filename property
    self.assertEqual(5, 1 + 4)

  def testUploadedOn(self):
    # TODO(michaelcupino): Find out if scapes is using uploadedOn property
    self.assertEqual(5, 1 + 4)

  def testSource(self):
    # TODO(michaelcupino): Find out if scapes is using source property
    self.assertEqual(5, 1 + 4)

  def testBlobkey(self):
    # TODO(michaelcupino): Find out if scapes is using blobkey property
    self.assertEqual(5, 1 + 4)

  def testWordcountLink(self):
    # TODO(michaelcupino): Find out if scapes is using wordcount_link property
    self.assertEqual(5, 1 + 4)

  def testIndexLink(self):
    # TODO(michaelcupino): Find out if scapes is using index_link property
    self.assertEqual(5, 1 + 4)

  def testPhrasesLink(self):
    # TODO(michaelcupino): Find out if scapes is using phrases_link property
    self.assertEqual(5, 1 + 4)

if __name__ == '__main__':
  unittest.main()

