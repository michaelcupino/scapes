from scapesres import ScapesResource
import scapesgdocsfacade

class ScapesFolder(ScapesResource):
  """ScapesFolder represents a gdoc folder"""

  def __init__(self, *args, **kwargs):
    """Initializes the object"""

    super(ScapesFolder, self).__init__(*args, **kwargs)

  def getDocumentsResourceIDs(self):
    """Gets the documents associated with this folder

    Args:
      None

    Returns:
      A list of document resource IDs
    """

    self.setGdataAuth()
    documentUri = "/-/document"
    uri = '/feeds/default/private/full/' + self.resourceID
    documentFeed = scapesgdocsfacade.run(self.gdocs.GetResources,
        uri=uri + "/contents" + documentUri)

    documentResourceIDs = []
    for entry in documentFeed.entry:
      resourceID = entry.resource_id.text
      documentResourceIDs.append(resourceID)

    return documentResourceIDs
