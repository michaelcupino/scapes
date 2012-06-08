from scapesmodel import Revision
import ConfigParser
import gdata.gauth
from google.appengine.api import users

# Configure gdata
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
SETTINGS = {
  'APP_NAME': config.get('gdata_settings', 'APP_NAME'),
  'CONSUMER_KEY': config.get('gdata_settings', 'CONSUMER_KEY'),
  'CONSUMER_SECRET': config.get('gdata_settings', 'CONSUMER_SECRET'),
  'SCOPES': [config.get('gdata_settings', 'SCOPES')]
}

gdocs = gdata.docs.client.DocsClient(source = SETTINGS['APP_NAME'])

class ScapesRevision():
  """ScapesRevision represents a gdoc revision"""
  datastoreRevision = None

  def __init__(self, selfLink):
    """Initializes the object"""

    self.selfLink = selfLink
    revisionQuery = Revision.all()
    revisionQuery.filter("revisionNumber = ", self.selfLink)
    if (revisionQuery.count(1) == 0):
      self.datastoreRevision = Revision()
    else:
      self.datastoreRevision = revisionQuery.get()

  def getRevisionTextFromQueryResults(self, datastoreRevision,
      revisionSelfLink):
    """Either downloads the reivsion text from the API or reterives the
    the revision from the datastore.

    Args:
      datastoreRevision: Revision. This can be None
      revisionSelfLink: String. Represents the self link of the revision
      
    Returns:
      String that contains the revision text
    """

    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    revisionText = None
    if (datastoreRevision.revisionDownloadedText is None):
      gdataRevision = gdocs.GetRevisionBySelfLink(self.selfLink)
      revisionText = gdocs.DownloadRevisionToMemory(
          gdataRevision, {'exportFormat': 'txt'})

      datastoreRevision.revisionNumber = revisionSelfLink
      datastoreRevision.revisionDownloadedText = revisionText
      datastoreRevision.put()

    else:
      revisionText = datastoreRevision.revisionDownloadedText

    return revisionText

  def getRevisionText(self):
    """Returns the revision text associated with this revision

    Args:
      None

    Returns:
      String that contains the revision text
    """

    revisionText = self.getRevisionTextFromQueryResults(self.datastoreRevision,
        self.selfLink)
    return revisionText

  def putWordsAdded(self, wordsAdded):
    """This puts the number of the words added for this revision to the
        datastore

    Args:
      Int. Represnts the number of words added

    Returns:
      None
    """

    self.datastoreRevision.wordsAdded = wordsAdded
    datastoreRevision.put()

  def putWordsDeleted(self, wordsDeleted):
    """This puts the number of the words deleted for this revision to the
        datastore

    Args:
      wordsDeleted: Int. Represnts the number of words deleted

    Returns:
      None
    """

    self.datastoreRevision.wordsDeleted = wordsDeleted
    datastoreRevision.put()

  def putWordCount(self, wordCount):
    """This puts the word count for this revision to the datastore

    Args:
      wordCount: Int. Represnts the word count

    Returns:
      None
    """

    self.datastoreRevision.wordCount = wordCount
    datastoreRevision.put()
