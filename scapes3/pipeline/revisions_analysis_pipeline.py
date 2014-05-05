from mapreduce import base_handler

class RevisionsAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline that analyzes two revisions and returns the number of words
  added and number of words deleted.
  """
  
  def run(self):
    raise NotImplementedError('Pipeline must be implemented.')

