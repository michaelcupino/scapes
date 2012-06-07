from scapesres import ScapesResource

class ScapesFolder(ScapesResource):
  """ScapesFolder represents a gdoc folder"""
  name = None

  def __init__(self):
    """Initializes the object"""

    print "ScapesFolder.__init__()"
    pass

  def getDocuments(self):
    """Gets the documents associated with this folder
    
    Args:
     
    Returns:
      A list of ScapesDocument
    """

    print "ScapesFolder.getDocuments()"

