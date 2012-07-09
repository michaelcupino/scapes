import csv
import logging
import tempfile
from gfolderanalyzer import GFolderAnalyzer
from google.appengine.ext import deferred
from scapesmodel import Revision

class CsvFolderExporter(object):
  """This class deals with CSV (for now, only CSV) exporting
  In the future, this class should be a subclass of a Exporter parent class
  because of document-exporters.
  """

  def __init__(self, folderResourceID, requesterUserID):
    """Initializes the object"""

    self.listeners = []
    self.firingInfo = {}
    self.folderResourceID = folderResourceID
    self.requesterUserID = requesterUserID

  def run(self):
    """Starts the folder exporting process"""

    folderAnalyzer = GFolderAnalyzer(self.folderResourceID,
        self.requesterUserID)
    folderAnalyzer.addListener(self)
    folderAnalyzer.analyze()

  def getCsvFile(self, documentsResourceIDs):
    """Creates and returns the CSV file"""

    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("CsvFolderExporter.getCsvFile(documentsResourceIDs)")
    logging.debug(documentsResourceIDs)

    csvFile = tempfile.TemporaryFile()
    writer = csv.writer(csvFile)
    values = [['Date', 'Time', 'Who in doc', 'Word count', 'Words added',
        'Words deleted', 'Punct. cap', 'Words moved', 'Document ID', 'Document Name']]
    writer.writerows(values)

    for documentResourceID in documentsResourceIDs:
      datastoreRevisionsQuery = Revision.all().filter("documentID =",
          documentResourceID)
      datastoreRevisionsQuery.order('date')
      datastoreRevisionsQuery.order('time')

      for datastoreRevision in datastoreRevisionsQuery:
        values = [[datastoreRevision.date, datastoreRevision.time,
            datastoreRevision.author, datastoreRevision.wordCount,
            datastoreRevision.wordsAdded, datastoreRevision.wordsDeleted,
            '-', '-', datastoreRevision.documentID,
            datastoreRevision.documentName]]
        writer.writerows(values)

    csvFile.seek(0)
    csvFileBytes = csvFile.read()
    csvFile.close()
    # TODO: Store the bytes into the datastore, so the user can choose to
    # redownload the analysis at a certain time

    return csvFileBytes

  def notify(self, firingInfo):
    """This function gets called with the analyzer is done doing its work"""

    documentsResourceIDs = firingInfo["documentsResourceIDs"]
    self.firingInfo["folderCsvExportFile"] = self.getCsvFile(documentsResourceIDs)
    self.firingInfo["folderTitle"] = firingInfo["folderTitle"]
    self.fireDoneAnalyzing()

  def addListener(self, listener):
    """Adds a listener. This listener will be notified when the analysis is
    complete
    """

    self.listeners.append(listener)

  def fireDoneAnalyzing(self):
    """Notify the listeners that analysis is finished"""

    for listener in self.listeners:
      deferred.defer(listener.notify, self.firingInfo)
