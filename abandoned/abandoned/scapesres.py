import ConfigParser
import gdata.docs.client
import scapesgdocsfacade

class ScapesResource(object):
  """ScapesResource is the parent class"""

  def getGdocsClient(self):
    """Gets the gdocs client"""

    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    SETTINGS = {
      'APP_NAME': config.get('gdata_settings', 'APP_NAME'),
      'CONSUMER_KEY': config.get('gdata_settings', 'CONSUMER_KEY'),
      'CONSUMER_SECRET': config.get('gdata_settings', 'CONSUMER_SECRET'),
      'SCOPES': [config.get('gdata_settings', 'SCOPES')]
    }

    return gdata.docs.client.DocsClient(source = SETTINGS['APP_NAME'])

  def __init__(self, *args, **kwargs):
    """Initializes the object

    Args:
      resourceID: the ID of the resource
      requesterUserID: the ID of the user

    TODO: Figure out this initialization arguments stuff
    """

    self.resourceID = args[0]
    self.requesterUserID = args[1]
    self.gdataResource = None
    self.gdocs = self.getGdocsClient()

  def setGdataAuth(self):
    """Sets the authorization for gdata"""

    access_token_key = 'access_token_%s' % self.requesterUserID
    access_token = gdata.gauth.AeLoad(access_token_key)
    self.gdocs.auth_token = access_token

  def getGdataResource(self):
    """Gets the gdataResource"""

    if self.gdataResource is None:
      self.setGdataAuth()
      self.gdataResource = scapesgdocsfacade.run(self.gdocs.GetResourceById,
          self.resourceID)

    return self.gdataResource

  def getTitle(self):
    """Gets the title of the resource"""

    gdataResource = self.getGdataResource()
    resourceTitle = gdataResource.title.text
    return resourceTitle
