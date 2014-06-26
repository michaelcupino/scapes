import urllib2

from mapreduce import base_handler

class RevisionFetcherPipeline(base_handler.PipelineBase):
  """A pipeline that fetches the revision text from a web resource.

  Args:
    exportLink: The export link of one resource that contains the actual text
      in a revision.

  Returns:
    The actual text in a revision.
  """
  
  def run(self, exportLink):
    return urllib2.urlopen(exportLink).read()

