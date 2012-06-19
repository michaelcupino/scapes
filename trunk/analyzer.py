import uuid
from google.appengine.ext import db
from scapesmodel import AnalyzerTracker
from sets import Set

class Analyzer(object):
  """Analyzer is the parent class"""

  def __init__(self):
    """Initializes the object"""

    self.listeners = []
    self.firingInfo = {}
    self.analyzerID = str(uuid.uuid1())

  def addListener(self, listener):
    """Adds a listener. This listener will be notified when the analysis is
    complete
    """

    self.listeners.append(listener)

  def fireDoneAnalyzing(self):
    """Notify the listeners that analysis is finished"""

    for listener in self.listeners:
      listener.notify(self.firingInfo)

  def getFinishedAnalyzedIDs(self):
    """Gets the set of IDs of the objects that have been analyzed"""

    analyzerTrackerQuery = AnalyzerTracker.all(keys_only = True)
    analyzerTrackerQuery.filter("analyzerID = ", self.analyzerID)
    finishedAnalyzedIDs = Set()
    for analyzerTrackerKey in analyzerTrackerQuery:
      analyzerTracker = AnalyzerTracker.get(analyzerTrackerKey)
      finishedAnalyzedIDs.add(
          analyzerTracker.analyzedID.encode())
    return finishedAnalyzedIDs

  def addFinishedAnalyzedIDToAnalyzerTracker(self, analyzedID):
    """Adds an ID to the analyzer tracker"""

    tracker = None
    analyzerTrackerQuery = AnalyzerTracker.all(keys_only = True)
    analyzerTrackerQuery.filter("analyzerID = ", self.analyzerID)
    analyzerTrackerQuery.filter("analyzedID = ", analyzedID)
    if (analyzerTrackerQuery.count(1) == 0):
      tracker = AnalyzerTracker()
      tracker.analyzerID = self.analyzerID
      tracker.analyzedID = analyzedID
      tracker.put()

  def cleanupAnalyzerTracker(self):
    """Cleans up the analyzer tracker by removing it from the datastore"""

    analyzerTrackerQuery = AnalyzerTracker.all(keys_only = True)
    analyzerTrackerQuery.filter("analyzerID = ", self.analyzerID)
    db.delete(analyzerTrackerQuery)
