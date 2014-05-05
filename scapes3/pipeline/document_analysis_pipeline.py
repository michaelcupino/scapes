from mapreduce import base_handler

class DocumentAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline that analyzes a document and persists its analysis.
  """
  
  def run(self):
    raise NotImplementedError('Pipeline must be implemented.')

