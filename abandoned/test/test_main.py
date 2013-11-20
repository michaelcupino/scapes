import unittest
import difflib
import diff_match_patch.diff_match_patch

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
from main import RequestRevision


gdiff = diff_match_patch.diff_match_patch()

# http://docs.python.org/library/test.html#writing-tests
# http://code.google.com/p/gaeunit/wiki/Readme
# http://code.google.com/appengine/docs/python/tools/localunittesting.html#Writing_Datastore_and_Memcache_Tests

class TestRevisionModel(db.Model):
  resourceLink = db.StringProperty()
  revisionNumber = db.StringProperty()
  revisionDownloadedText = db.BlobProperty()

class MainTest(unittest.TestCase):

  def setUp(self):
    self.requestObject = RequestRevision()

  def testIsRemove(self):
    x = self.requestObject.isRemove([gdiff.DIFF_DELETE, "STUFF DELETED HERE"])
    self.assertTrue(x)
    y = self.requestObject.isRemove([gdiff.DIFF_INSERT, "STUFF ADDED HERE"])
    self.assertFalse(y)

