from scapesres import ScapesResource
from datetime import datetime
from scapesmodel import Revision
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

class ScapesDocument(ScapesResource):
  """ScapesDocument represents a gdoc document"""
  name = None

  def __init__(self, resourceID):
    """Initializes the object"""
    
    self.resourceID = resourceID

  def getRevisionsSelfLinks(self):
    """Gets the self links of the revisions associated with this document

    Args:

    Returns:
      A list of self links
    """
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    resource = gdocs.GetResourceById(self.resourceID)
    revisions = gdocs.GetRevisions(resource)
    
    scapesRevisionIDs = []
    
    for revision in revisions.entry:
      scapesRevisionIDs.append(revision.GetSelfLink().href)
      
    return scapesRevisionIDs
        