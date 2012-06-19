import logging
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

  def __init__(self, resourceID, requesterUserID):
    """Initializes the object"""

    self.resourceID = resourceID
    self.requesterUserID = requesterUserID
    self.gdataResource = None

  def getGdataResource(self):
    """Gets the gdataResource"""

    if self.gdataResource is None:
      access_token_key = 'access_token_%s' % self.requesterUserID
      access_token = gdata.gauth.AeLoad(access_token_key)
      gdocs.auth_token = access_token
      self.gdataResource = gdocs.GetResourceById(self.resourceID)

    return self.gdataResource

  def getRevisionsSelfLinks(self):
    """Gets the self links of the revisions associated with this document

    Args:

    Returns:
      A list of self links
    """

    gdataResource = self.getGdataResource()
    revisions = gdocs.GetRevisions(gdataResource)

    scapesRevisionIDs = []

    for revision in revisions.entry:
      scapesRevisionIDs.append(revision.GetSelfLink().href)


    return scapesRevisionIDs

  def getTitle(self):
    """Gets the title of the document"""

    gdataResource = self.getGdataResource()
    documentTitle = gdataResource.title.text
    return documentTitle
