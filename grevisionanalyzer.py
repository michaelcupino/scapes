import logging
import string
from analyzer import Analyzer
from google.appengine.ext import deferred
from scapesrev import ScapesRevision

class GRevisionAnalyzer(Analyzer):
  """GRevisionAnalyzer contains the logic to analyze a revision"""

  def __init__(self, revisionSelfLink, requesterUserID):
    """Initializes the object"""

    super(GRevisionAnalyzer, self).__init__()
    self.revisionSelfLink = revisionSelfLink
    self.firingInfo["revisionSelfLink"] = self.revisionSelfLink
    self.requesterUserID = requesterUserID

  def analyze(self):
    """Analyze the revision"""

    deferred.defer(self.fetchRevisionText, self.revisionSelfLink,
        self.requesterUserID)

  def fetchRevisionText(self, revisionSelfLink, requesterUserID):
    """Get the revision text, so we can do some analysis"""

    scapesRevision = ScapesRevision(revisionSelfLink, requesterUserID)
    revisionText = scapesRevision.getRevisionText()
    deferred.defer(self.doneFetchingRevisionText, revisionText,
        scapesRevision)

  def getWordCount(self, revisionText):
    """Counts the number of words in a String

    Args:
     revisionText: String. Text of the revision.

    Returns:
      Int. Number of words in revisionText.
    """

    revisionText = string.split(revisionText, '\n')
    wordCount = 0;
    for line in revisionText:
      line = line.split()
      wordCount = wordCount + len(line)
    return wordCount

  def doneFetchingRevisionText(self, revisionText, scapesRevision):
    """Count the number of words, and put the word count into the
    scapesRevision
    """

    revisionWordCount = self.getWordCount(revisionText)
    scapesRevision.putWordCount(revisionWordCount)
    revisionAuthors = scapesRevision.getAuthors()
    revisionDate = scapesRevision.getDate()
    revisionTime = scapesRevision.getTime()

    self.fireDoneAnalyzing()
