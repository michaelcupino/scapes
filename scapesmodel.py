from google.appengine.ext import db

class Revision(db.Model):
  resourceLink = db.StringProperty() # Redundant
  revisionNumber = db.StringProperty()
  revisionDownloadedText = db.BlobProperty()
  date = db.DateProperty()
  time = db.TimeProperty()
  author = db.EmailProperty()
  wordCount = db.IntegerProperty()
  wordsAdded = db.IntegerProperty()
  wordsDeleted = db.IntegerProperty()
