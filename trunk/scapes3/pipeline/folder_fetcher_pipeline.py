from mapreduce import base_handler

class FolderFetcherPipeline(base_handler.PipelineBase):
  """A pipeline that returns all the Google Doc ids inside the folder plus all
  the Google Doc ids inside subfolders.
  """
  
  def run(self):
    raise NotImplementedError('Pipeline must be implemented.')

