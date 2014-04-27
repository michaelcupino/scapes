from datetime import datetime
from scapesmodel import Revision
import ConfigParser
import gdata.docs.client
import gdata.gauth
import scapesgdocsfacade

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

  def __init__(self, selfLink, requesterUserID):
    """Initializes the object"""

    self.selfLink = selfLink
    self.requesterUserID = requesterUserID
    self.datastoreRevision = None
    self.gdataRevision = None

    revisionQuery = Revision.all(keys_only = True)
    revisionQuery.filter("revisionNumber = ", self.selfLink)
    if (revisionQuery.count(1) == 0):
      self.datastoreRevision = Revision()
      self.datastoreRevision.revisionNumber = selfLink
      self.datastoreRevision.put()
    else:
      self.datastoreRevision = Revision.get(revisionQuery.get())

  def setGdataAuth(self):
    """Sets the authorization for gdata"""

    access_token_key = 'access_token_%s' % self.requesterUserID
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

  def getGdataRevision(self):
    """Gets the gdata revision"""

    if self.gdataRevision is None:
      self.setGdataAuth()
      self.gdataRevision = scapesgdocsfacade.run(gdocs.GetRevisionBySelfLink,
          self.selfLink)


    return self.gdataRevision

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

    revisionText = None
    if (datastoreRevision.revisionDownloadedText is None):
      gdataRevision = self.getGdataRevision()
      revisionText = scapesgdocsfacade.run(gdocs.DownloadRevisionToMemory,
          gdataRevision, {'exportFormat': 'txt'})
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

  def getAuthors(self):
    """Returns the authors associated with the revision. At the time of
    implementation, the gdata library only returns one author for any revision,
    even revisions with multiple authors."""

    revisionAuthors = None
    if (self.datastoreRevision.author is None):
      gdataRevision = self.getGdataRevision()
      if len(gdataRevision.author) > 0:
        revisionAuthorsRaw = gdataRevision.author[0].email
        if revisionAuthorsRaw is None:
          revisionAuthors = "anonymous (Anyone with link. No sign-in required.)"
        else:
          revisionAuthors = revisionAuthorsRaw.text
      else:
        revisionAuthor = "No author"
      self.datastoreRevision.author = revisionAuthors
      self.datastoreRevision.put()

    else:
      revisionAuthors = self.datastoreRevision.author

    return revisionAuthors

  def getDateTimeOfGdataRevision(self, gdataRevision):
    """Returns the datetime object associated with this revision"""

    return datetime.strptime(gdataRevision.updated.text,
        "%Y-%m-%dT%H:%M:%S.%fZ")

  def getDate(self):
    """Returns the date that the revision was created. It's still unknown
    what timezone the dates are in"""

    revisionDate = None
    if (self.datastoreRevision.date is None):
      gdataRevision = self.getGdataRevision()
      revisionLastEditedDateTime = self.getDateTimeOfGdataRevision(gdataRevision)
      revisionDate = revisionLastEditedDateTime.date()
      self.datastoreRevision.date = revisionDate
      self.datastoreRevision.time = revisionLastEditedDateTime.time()
      self.datastoreRevision.put()

    else:
      revisionDate = self.datastoreRevision.date

    return revisionDate

  def getTime(self):
    """Returns the time that the revision was created. It's still unknown
    what timezone the times are in"""

    revisionTime = None
    if (self.datastoreRevision.time is None):
      gdataRevision = self.getGdataRevision()
      revisionLastEditedDateTime = self.getDateTimeOfGdataRevision(gdataRevision)
      self.datastoreRevision.date = revisionLastEditedDateTime.date()
      revisionTime = revisionLastEditedDateTime.time()
      self.datastoreRevision.time = revisionTime
      self.datastoreRevision.put()

    else:
      revisionTime = self.datastoreRevision.time

    return revisionTime

  def putWordsAdded(self, wordsAdded):
    """This puts the number of the words added for this revision to the
        datastore

    Args:
      Int. Represnts the number of words added

    Returns:
      None
    """

    self.datastoreRevision.wordsAdded = wordsAdded
    self.datastoreRevision.put()

  def putWordsDeleted(self, wordsDeleted):
    """This puts the number of the words deleted for this revision to the
        datastore

    Args:
      wordsDeleted: Int. Represnts the number of words deleted

    Returns:
      None
    """

    self.datastoreRevision.wordsDeleted = wordsDeleted
    self.datastoreRevision.put()

  def putWordCount(self, wordCount):
    """This puts the word count for this revision to the datastore

    Args:
      wordCount: Int. Represnts the word count

    Returns:
      None
    """

    self.datastoreRevision.wordCount = wordCount
    self.datastoreRevision.put()

  def putDocumentResourceID(self, documentResourceID):
    """This puts the document resource ID of the document of the revision"""

    self.datastoreRevision.documentID = documentResourceID
    self.datastoreRevision.put()

  def putDocumentTitle(self, documentTitle):
    """This puts the document title of the revision"""

    self.datastoreRevision.documentName = documentTitle
    self.datastoreRevision.put()
