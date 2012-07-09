from scapesres import ScapesResource
import scapesgdocsfacade

class ScapesDocument(ScapesResource):
  """ScapesDocument represents a gdoc document"""

  def __init__(self, *args, **kwargs):
    """Initializes the object"""

    super(ScapesDocument, self).__init__(*args, **kwargs)

  def getRevisionsSelfLinks(self):
    """Gets the self links of the revisions associated with this document

    Args:

    Returns:
      A list of self links
    """

    gdataResource = self.getGdataResource()
    revisions = scapesgdocsfacade.run(self.gdocs.GetRevisions, gdataResource)

    scapesRevisionIDs = []
    for revision in revisions.entry:
      scapesRevisionIDs.append(revision.GetSelfLink().href)

    return scapesRevisionIDs

