import logging
from google.appengine.ext import db
from google.appengine.ext import deferred
from scapesmodel import AnalyzerTracker
from sets import Set

class Analyzer(object):
  """Analyzer is the parent class"""

  def __init__(self):
    """Initializes the object"""

    self.listeners = []
    self.firingInfo = {}
    self.analyzerTracker = AnalyzerTracker()
    self.analyzerTracker.put()
    self.analyzerID = str(self.analyzerTracker.key())

  def addListener(self, listener):
    """Adds a listener. This listener will be notified when the analysis is
    complete
    """

    self.listeners.append(listener)

  def fireDoneAnalyzing(self):
    """Notify the listeners that analysis is finished"""

    for listener in self.listeners:
      deferred.defer(listener.notify, self.firingInfo)

  @db.transactional
  def getFinishedAnalyzedIDs(self):
    """Gets the set of IDs of the objects that have been analyzed"""

    # TODO: Figure out why this returns more than the ancestors of the
    # specified key. The query also returns the ancestor itself.
    analyzerTrackerQuery = db.Query().ancestor(self.analyzerTracker.key())
    finishedAnalyzedIDs = Set()
    for analyzerTracker in analyzerTrackerQuery:
      if analyzerTracker.key().name():
        finishedAnalyzedIDs.add(analyzerTracker.key().name().encode())
    return finishedAnalyzedIDs

  @db.transactional
  def addFinishedAnalyzedIDToAnalyzerTracker(self, analyzedID):
    """Adds an ID to the analyzer tracker"""

    tracker = AnalyzerTracker.get_by_key_name(analyzedID,
        parent = self.analyzerTracker)
    if tracker is None:
      tracker = AnalyzerTracker(key_name = analyzedID,
          parent = self.analyzerTracker)
      tracker.put()

  def cleanupAnalyzerTracker(self):
    """Cleans up the analyzer tracker by removing it from the datastore"""

    analyzerTrackerQuery = db.Query().ancestor(self.analyzerTracker.key())
    db.delete(analyzerTrackerQuery)
