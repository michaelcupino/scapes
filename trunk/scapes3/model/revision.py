from google.appengine.ext import ndb

class Revision(ndb.Model):
  documentID = ndb.StringProperty()
  documentName = ndb.StringProperty()
  revisionNumber = ndb.StringProperty()
  revisionDownloadedText = ndb.BlobProperty()
  date = ndb.DateProperty()
  time = ndb.TimeProperty()
  author = ndb.StringProperty()
  wordCount = ndb.IntegerProperty()
  wordsAdded = ndb.IntegerProperty()
  wordsDeleted = ndb.IntegerProperty()

