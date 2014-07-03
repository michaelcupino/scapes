from google.appengine.ext import ndb

class Revision(ndb.Model):
  documentId = ndb.StringProperty()
  documentName = ndb.StringProperty()
  revisionNumber = ndb.StringProperty()
  date = ndb.DateProperty()
  time = ndb.TimeProperty()
  dateTime = ndb.StringProperty()
  author = ndb.StringProperty()
  wordCount = ndb.IntegerProperty()
  wordsAdded = ndb.IntegerProperty()
  wordsDeleted = ndb.IntegerProperty()
  exportLink = ndb.StringProperty()

