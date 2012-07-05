import logging
from analyzer import Analyzer
from gdocumentanalyzer import GDocumentAnalyzer
from google.appengine.ext import db
from google.appengine.ext import deferred
from scapesfolder import ScapesFolder
from sets import Set

class GFolderAnalyzer(Analyzer):
  """GFolderAnalyzer contains the logic to analyze a folder"""

  def __init__(self, folderResourceID, requesterUserID):
    """Initializes the object"""

    super(GFolderAnalyzer, self).__init__()
    self.folderResourceID = folderResourceID
    self.firingInfo["folderResourceID"] = self.folderResourceID
    self.requesterUserID = requesterUserID
    self.fetchedDocumentsResourceIDs = None

  def notify(self, firingInfo):
    """This function is called when a document is finished being analyzed"""

    documentResourceID = firingInfo["documentResourceID"]
    self.addFinishedAnalyzedIDToAnalyzerTracker(documentResourceID)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("GFolderAnalyzer.notify(firingInfo)")
    areAllFinished = self.areAllDocumentsFinishedBeingAnalyzed()
    logging.debug(areAllFinished)
    logging.debug(self.fetchedDocumentsResourceIDs)

    if areAllFinished:
      self.fireDoneAnalyzing()
      self.cleanupAnalyzerTracker()

  def areAllDocumentsFinishedBeingAnalyzed(self):
    """Check if all documents are done being analyzed"""

    logging.getLogger().setLevel(logging.DEBUG)
    finishedAnalyzed = self.getFinishedAnalyzedIDs()
    logging.debug(finishedAnalyzed)
    return self.fetchedDocumentsResourceIDs == finishedAnalyzed

  def analyze(self):
    """Starts the analysis of the folder by making async calls"""

    deferred.defer(self.fetchDocuments, self.folderResourceID,
        self.requesterUserID)

  def fetchDocuments(self, folderResourceID, requesterUserID):
    """Fetch the document IDs of the documents inside the folder"""

    folder = ScapesFolder(folderResourceID)
    self.fetchedDocumentsResourceIDs = Set(folder.getDocumentsResourceIDs(
        requesterUserID))
    deferred.defer(self.doneFetchingListOfDocumentsIDs,
        self.fetchedDocumentsResourceIDs, requesterUserID)

  def doneFetchingListOfDocumentsIDs(self, scapesDocumentsResourceIDs,
      requesterUserID):
    """Create GDocumentAnalyzers for each of the document id, and start
    analyzing them
    """

    for scapesDocumentResourceID in scapesDocumentsResourceIDs:
      documentAnalyzer = GDocumentAnalyzer(scapesDocumentResourceID,
          requesterUserID)
      documentAnalyzer.addListener(self)
      documentAnalyzer.analyze()
