from scapesres import ScapesResource

class ScapesRevision(ScapesResource):
  """ScapesRevision represents a gdoc revision"""
  name = None

  def __init__(self):
    """Initializes the object"""

    print "ScapesResource.__init__()"
    pass

  def getRevisionText(self):
    """Gets the revision text

    Args:

    Returns:
      Returns the revision text
    """

    print "ScapesRevision.getRevisionText()"
