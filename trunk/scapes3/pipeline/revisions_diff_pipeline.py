from mapreduce import base_handler
from model.revision import Revision

class RevisionsDiffPipeline(base_handler.PipelineBase):
  """A pipeline that calculates the words added and the words removed between
  two texts.

  Args:
    exportLinks: The export links of a resources that contains the actual text
      in a revision.

  Returns:
    Temporarily returns a number that represents how many characters have been
    added or removed. This will eventually return a ScapesDiff object that
    contains how many words were added and removed.
  """
  
  def run(self, revisionTextA, revisionTextB):
    # TODO(michaelcupino): Actually calculate the diff between the two texts.
    revision = Revision()
    revision.wordsAdded = 25
    revision.wordsDeleted = len(revisionTextB) - len(revisionTextA)
    return revision.to_dict()

