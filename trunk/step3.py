import ConfigParser
import gdata.gauth
import jinja2
import os
import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required


# TODO: Find out if we can have only one reference of this
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

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


class FetchRevision(webapp2.RequestHandler):
  def replaceFirstToken(self, text):
    """This replaces the first token to 'Folders'. The reason for this is
    because the API does not return what we would have expected (specifically
    in the folder feed title).
    """
    textList = text.split();
    if textList[0] == 'Documents':
      textList[0] = 'Folders'
      text = ' '.join(textList)
    return text

  @login_required
  def get(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    # TODO(mcupino): AJAXify this
    folderResourceId = self.request.get('resource')
    documentUri = "/-/document"
    uri = '/feeds/default/private/full'
    if folderResourceId:
      showFolders = True
      uri = '/feeds/default/private/full/' + folderResourceId
      documentFeed = gdocs.GetResources(uri=uri + "/contents" + documentUri)
    else:
      showFolders = False
      documentFeed = gdocs.GetResources(uri=uri + documentUri)
    
    documentListTitle = documentFeed.title.text
    folderListTitle = ""
    documents = []
    folders = []
    resourceLinks = []
    for entry in documentFeed.entry:
      resourceLink = entry.GetSelfLink().href
      resourceLinks.append(resourceLink)
      documentTuple = {
        'entry': entry,
      }
      documents.append(documentTuple)

    if showFolders:
      folderUri = "/-/folder"
      folderFeed = gdocs.GetResources(uri=uri + "/contents" + folderUri)
      folderListTitle = self.replaceFirstToken(folderFeed.title.text)
      for entry in folderFeed.entry:
        folder = {
          'title': entry.title.text,
          'id': entry.resource_id.text
        }
        folders.append(folder)
      showFolders = showFolders and folders
     
    # TODO: Add a TODO, saying that eventually we want to give the resource 
    # links of a folder, instead of all the resource links of the docs in the folder.
    
    # Appends resourceLinks for table download
    tableDownloadLink = ""
    count = 1
    for resourceLink in resourceLinks:
      resourceLinkSubStart = resourceLink.find("/folder")
      resourceLinkSubEnd = resourceLink.find("/document")
      newResourceLink = resourceLink[:resourceLinkSubStart] + resourceLink[resourceLinkSubEnd:]
      if tableDownloadLink == "":
        tableDownloadLink = newResourceLink
      else:
        tableDownloadLink = tableDownloadLink + "&resourceSelfLink" + str(count) + "=" + newResourceLink
      count += 1

    templateValues = {
      'entries': documents,
      'resourceLinks': resourceLinks,
      'showFolders': showFolders,
      'folders': folders,
      'folderListTitle': folderListTitle,
      'documentListTitle': documentListTitle,
      'tableDownloadLink': tableDownloadLink
    }
    template = jinja_environment.get_template('templates/step3.html')
    self.response.out.write(template.render(templateValues))

