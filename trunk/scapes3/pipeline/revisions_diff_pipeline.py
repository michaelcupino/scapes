from mapreduce import base_handler

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
    return len(revisionTextB) - len(revisionTextA)

