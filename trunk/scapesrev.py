from scapesres import ScapesResource

class ScapesRevision(ScapesResource):
  """ScapesRevision represents a gdoc revision"""
  name = None
  author = None
  date = None
  time = None
  revisionText = None
  wordCount = None
  wordsAdded = None
  wordsDeleted = None

  def __init__(self, selfLink):
    """Initializes the object"""
    ScapesResource.resourceID = selfLink
    
  def putWordsAdded(self, added):
    wordsAdded = added
    
  def putWordsDeleted(self, removed):
    wordsDeleted = removed
    
  def putWordCount(self, count):
    wordCount = count