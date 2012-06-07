from scapesres import ScapesResource

class ScapesDocument(ScapesResource):
  """ScapesDocument represents a gdoc document"""
  name = None

  def __init__(self):
    """Initializes the object"""

    print "ScapesDocument.__init__()"
    pass

  def getRevisions(self):
    """Gets the revisions associated with this document

    Args:

    Returns:
      A list of ScapesRevision
    """

    print "ScapesDocument.getRevisions()"
