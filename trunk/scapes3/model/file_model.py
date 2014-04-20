from google.appengine.ext import ndb

class File(ndb.Model):
    """Models an individual File entry with author, content and date."""
    author = ndb.UserProperty()
    list_of_id = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

