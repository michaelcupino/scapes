from mapreduce import base_handler

class FolderAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline that analyzes a folder and emails its analysis to the requester.
  """
  
  def run(self):
    raise NotImplementedError('Pipeline must be implemented.')

