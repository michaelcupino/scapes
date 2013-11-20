import ConfigParser
import csv
import gdata.gauth
import webapp2
import urllib
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from scapesmodel import Revision


config = ConfigParser.RawConfigParser()
config.read('config.cfg')
SETTINGS = {
  'APP_NAME': config.get('gdata_settings', 'APP_NAME'),
  'CONSUMER_KEY': config.get('gdata_settings', 'CONSUMER_KEY'),
  'CONSUMER_SECRET': config.get('gdata_settings', 'CONSUMER_SECRET'),
  'SCOPES': [config.get('gdata_settings', 'SCOPES')]
}

# TODO: Generate a gdocs object from a singleton
gdocs = gdata.docs.client.DocsClient(source = SETTINGS['APP_NAME'])

class CsvExportRequestHandler(webapp2.RequestHandler):
  def setAuth(self):
    """Creates the auth to look at docs".

    Args:
      None

    Returns:
      Does not return anything
    """
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token
    
  def getSelfLinks(self, folderResourceId, resourceLink):
    """Gets a list of self links from either folderResourceId or resourceLink".

    Args:
      folderResourceId: folder resource ID from url or None
      resourceLink: document resource link or None

    Returns:
      Returns a list of self links 0 to many
    """
    documentUri = "/-/document"
    uri = '/feeds/default/private/full'
    listOfSelfLinks = []
    if folderResourceId:
      uri = '/feeds/default/private/full/' + folderResourceId
      documentFeed = gdocs.GetResources(uri=uri + "/contents" + documentUri)
      
      for entry in documentFeed.entry:
        resourceLink = entry.GetSelfLink().href
        resourceLinkSubStart = resourceLink.find("/folder")
        resourceLinkSubEnd = resourceLink.find("/document")
        newResourceLink = resourceLink[:resourceLinkSubStart] + resourceLink[resourceLinkSubEnd:]
        listOfSelfLinks.append(urllib.unquote(newResourceLink))
    elif resourceLink:
      listOfSelfLinks.append(resourceLink)
    return listOfSelfLinks
      
  def writeValues(self, listOfSelfLinks):
    """Writes the wanted values from the self links".

    Args:
      listOfSelfLinks: list of self links used to write values

    Returns:
      Returns a boolean if csv is ready for download
    """
    writer = csv.writer(self.response.out)
    values = [['Date', 'Time', 'Who in doc', 'Word count', 'Words added',
        'Words deleted', 'Punct. cap', 'Words moved', 'Document ID', 'Document Name']]
    writer.writerows(values)
    
    isCsvReadyForDownload = True
    for selfLink in listOfSelfLinks:
      allRevisionsQuery = Revision.all(keys_only=True)
      revisionsOfResourceQuery = allRevisionsQuery.filter("resourceLink = ",
          selfLink)
      if revisionsOfResourceQuery.count() > 0:
        revisionsOfResourceQuery.order('date')
        revisionsOfResourceQuery.order('time')

        for revisionKey in revisionsOfResourceQuery:
          revision = Revision.get(revisionKey)
          values = [[revision.date, revision.time, revision.author,
              revision.wordCount, revision.wordsAdded, revision.wordsDeleted,
              '-', '-', revision.documentID, revision.documentName]]
          writer.writerows(values)
      else:
        isCsvReadyForDownload = False
        taskqueue.add(
            url = '/step4',
            params = {
                'documentSelfLink': selfLink,
                 'userId': users.get_current_user().user_id()
                }
        )

    return isCsvReadyForDownload
        
        
    
  def getFileName(self, folderResourceId, resourceLink):
    """Gets the file name of the csv based on documents".

    Args:
      folderResourceId: 
      resourceLink:

    Returns:
      Returns the titles of the .csv
    """
    # TODO: Somehow get the title
    return "export"

  @login_required
  def get(self):
  
    self.setAuth()
  
    folderResourceId = self.request.get('folderResourceId')
    resourceLink = self.request.get('resourceSelfLink')
    listOfSelfLinks = self.getSelfLinks(folderResourceId, resourceLink)
    
    isCsvReadyForDownload = self.writeValues(listOfSelfLinks)
    if isCsvReadyForDownload:
      csvFilename = self.getFileName(folderResourceId, resourceLink)
      self.response.headers['Content-Type'] = "text/csv"
      self.response.headers['Content-Disposition'] = "attachment; " + "filename=" + csvFilename + ".csv"
    else:
      self.response.out.write('<script>alert("Not ready for download");</script>')
