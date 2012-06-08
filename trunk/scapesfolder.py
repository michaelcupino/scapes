from scapesres import ScapesResource
import ConfigParser
import gdata.gauth
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required

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

class ScapesFolder(ScapesResource):
  """ScapesFolder represents a gdoc folder"""
  name = None

  def __init__(self, resourceID):
    """Initializes the object"""

    self.resourceID = resourceID

  def getDocumentsResourceIDs(self):
    """Gets the documents associated with this folder
    
    Args:
     
    Returns:
      A list of document resource IDs
    """
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token
    
    documentUri = "/-/document"
    uri = '/feeds/default/private/full/' + self.resourceID
    documentFeed = gdocs.GetResources(uri=uri + "/contents" + documentUri)
    
    documentResourceIDs = []
    
    for entry in documentFeed.entry:
      resourceID = entry.resource_id.text
        
      documentResourceIDs.append(resourceID)
       
    return documentResourceIDs