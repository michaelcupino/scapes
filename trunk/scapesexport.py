import csv
import webapp2
from google.appengine.ext.webapp.util import login_required
from scapesmodel import Revision

class CsvExportRequestHandler(webapp2.RequestHandler):
  @login_required
  def get(self):
    count = 1
    listOfSelfLinks = []
    moreLinks = True
    while moreLinks:
      resourceSelfLink = self.request.get('resourceSelfLink' + str(count))
      if resourceSelfLink == "":
        moreLinks = False
      else:
        listOfSelfLinks.append(resourceSelfLink)
      count += 1
    
    writer = csv.writer(self.response.out)
    values = [['Date', 'Time', 'Who in doc', 'Word count', 'Words added',
        'Words deleted', 'Punct. cap', 'Words moved', 'Document ID', 'Document Name']]
    writer.writerows(values)
    
    for selfLink in listOfSelfLinks:
      allRevisionsQuery = Revision.all(keys_only=True)
      revisionsOfResourceQuery = allRevisionsQuery.filter("resourceLink = ",
          selfLink)
      revisionsOfResourceQuery.order('date')
      revisionsOfResourceQuery.order('time')

      for revisionKey in revisionsOfResourceQuery:
        revision = Revision.get(revisionKey)
        values = [[revision.date, revision.time, revision.author,
            revision.wordCount, revision.wordsAdded, revision.wordsDeleted,
            '-', '-', revision.documentID, revision.documentName]]
        writer.writerows(values)

    # TODO: Somehow get the title
    csvFilename = str(Revision.get(revisionsOfResourceQuery.get()).author) + "-title"
    self.response.headers['Content-Type'] = "text/csv"
    self.response.headers['Content-Disposition'] = "attachment; " + "filename=" + csvFilename + ".csv"