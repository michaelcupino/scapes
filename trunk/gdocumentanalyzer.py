import diff_match_patch.diff_match_patch
import logging
from analyzer import Analyzer
from google.appengine.ext import deferred
from grevisionanalyzer import GRevisionAnalyzer
from scapesdocument import ScapesDocument
from scapesrev import ScapesRevision
from sets import Set

gdiff = diff_match_patch.diff_match_patch()

class GDocumentAnalyzer(Analyzer):
  """GDocumentAnalyzer contains the logic to analyze a document"""

  def __init__(self, documentResourceID, requesterUserID):
    """Initializes the object"""

    super(GDocumentAnalyzer, self).__init__()
    self.documentResourceID = documentResourceID
    self.firingInfo["documentResourceID"] = self.documentResourceID
    self.requesterUserID = requesterUserID
    self.fetchedRevisionsSelfLinks = None
    self.fetchedRevisionsSelfLinksList = None
    self.scapesDocument = None

  def isRemove(self, x):
    """Determines whether a gdiff tuple signifies a removal. Helps with
    with the filtering.
    """
    return x[0] == gdiff.DIFF_DELETE

  def isAdd(self, x):
    """Determines whether a gdiff tuple signifies an add. Helps with
    with the filtering.
    """
    return x[0] == gdiff.DIFF_INSERT

  def isRemoveOrAdd(self, x):
    """Determines whether a gdiff tuple signifies either an add or a removal.
    Helps with with the filtering.
    """
    return x[0] != gdiff.DIFF_EQUAL

  # TODO(mcupino): Make this into a separate higher level function, so
  # we don't have to do if elses for every time we reduce
  # TODO(mcupino): Don't count characters that were appended to a word
  # as a word added
  def addWordCount(self, x, y):
    """Adds "diff tuples" together. Helps with reducing."""
    if type(x) == type(1):
      return x + y[1]
    else:
      return x[1] + y[1]

  def countWords(self, x):
    """Counts the number of words in a String. Helps with mapping."""
    splitedString = x[1].split()
    wordCount = len(splitedString)
    return (x[0], wordCount)

  def getAddWordCount(self, diffWordCount):
    """Returns the word count of "added-diff tuples".

    Args:
      diffWordCount: [(operator, Int)] List of tuples

    Returns:
      Int. Number of words added.
    """
    newDiffsAdded = filter(self.isAdd, diffWordCount)
    if newDiffsAdded == []:
      return 0
    elif len(newDiffsAdded) == 1:
      return newDiffsAdded[0][1]
    else:
      return reduce(self.addWordCount, newDiffsAdded)

  def getDeletedWordCount(self, diffWordCount):
    """Returns the word count of "removed-diff tuples".

    Args:
      diffWordCount: [(operator, Int)] List of tuples

    Returns:
      Int. Number of words removed.
    """
    newDiffsRemoved = filter(self.isRemove, diffWordCount)
    if newDiffsRemoved == []:
      return 0
    elif len(newDiffsRemoved) == 1:
      return newDiffsRemoved[0][1]
    else:
      return reduce(self.addWordCount, newDiffsRemoved)

  def analyzeRevisionDiffs(self):
    """After all the revisions are fetched, let's start analyzing the diffs
    between each revision
    """

    previousRevisionText = ""
    for revisionSelfLink in self.fetchedRevisionsSelfLinksList:
      scapesRevision = ScapesRevision(revisionSelfLink, self.requesterUserID)
      currentRevisionText = scapesRevision.getRevisionText()

      revisionDiffs = gdiff.diff_main(previousRevisionText,
          currentRevisionText, False)
      gdiff.diff_cleanupSemantic(revisionDiffs)
      revisionDiffs = filter(self.isRemoveOrAdd, revisionDiffs)
      diffWordCount = map(self.countWords, revisionDiffs)
      addedWordCount = self.getAddWordCount(diffWordCount)
      deletedWordCount = self.getDeletedWordCount(diffWordCount)

      scapesDocument = self.getScapesDocument()
      documentTitle = scapesDocument.getTitle()

      scapesRevision.putWordsAdded(addedWordCount)
      scapesRevision.putWordsDeleted(deletedWordCount)
      scapesRevision.putDocumentResourceID(self.documentResourceID)
      scapesRevision.putDocumentTitle(documentTitle)

      logging.getLogger().setLevel(logging.DEBUG)
      logging.debug("documentTItle: %s" % documentTitle)

      previousRevisionText = currentRevisionText

    self.fireDoneAnalyzing()

  def notify(self, firingInfo):
    """This function is called when a revision is finished being analyzed"""

    revisionSelfLink = firingInfo["revisionSelfLink"]
    self.addFinishedAnalyzedIDToAnalyzerTracker(revisionSelfLink)
    if self.areAllRevisionsFinishedBeingAnalyzed():
      deferred.defer(self.analyzeRevisionDiffs)

  def areAllRevisionsFinishedBeingAnalyzed(self):
    """Finds out if all revisions are done being analyzed"""

    return self.getFinishedAnalyzedIDs() == self.fetchedRevisionsSelfLinks

  def analyze(self):
    """Analyze the document"""

    deferred.defer(self.fetchRevisions, self.documentResourceID,
        self.requesterUserID)

  def getScapesDocument(self):
    """Get scapes document object"""

    if self.scapesDocument is None:
      self.scapesDocument = ScapesDocument(self.documentResourceID,
          self.requesterUserID)

    return self.scapesDocument

  def fetchRevisions(self, documentResourceID, requesterUserID):
    """Get the self links of the revisions inside the documents"""

    scapesDocument = self.getScapesDocument()
    self.fetchedRevisionsSelfLinksList = scapesDocument.getRevisionsSelfLinks()
    self.fetchedRevisionsSelfLinks = Set(self.fetchedRevisionsSelfLinksList)
    deferred.defer(self.doneFetchingListOfRevisionsSelfLinks,
        self.fetchedRevisionsSelfLinks, requesterUserID)

  def doneFetchingListOfRevisionsSelfLinks(self, revisionsSelfLinks,
      requesterUserID):
    """Create revisions analyzers, and create analysis for each revisions"""

    for revisionSelfLink in revisionsSelfLinks:
      revisionAnalyzer = GRevisionAnalyzer(revisionSelfLink,
          requesterUserID)
      revisionAnalyzer.addListener(self)
      revisionAnalyzer.analyze()
