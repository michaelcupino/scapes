from scapesres import ScapesResource
import ConfigParser
import gdata.docs.client
import gdata.gauth
import scapesgdocsfacade

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

  def getDocumentsResourceIDs(self, userID):
    """Gets the documents associated with this folder

    Args:
      userID: The userID of the user that requested

    Returns:
      A list of document resource IDs
    """
    access_token_key = 'access_token_%s' % userID
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    documentUri = "/-/document"
    uri = '/feeds/default/private/full/' + self.resourceID
    documentFeed = scapesgdocsfacade.run(gdocs.GetResources,
        uri=uri + "/contents" + documentUri)

    documentResourceIDs = []

    for entry in documentFeed.entry:
      resourceID = entry.resource_id.text

      documentResourceIDs.append(resourceID)

    return documentResourceIDs
