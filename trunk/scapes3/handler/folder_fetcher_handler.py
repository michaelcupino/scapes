import webapp2

class FolderFetcherHandler(webapp2.RequestHandler):
  """Handler that starts the FolderFetcherPipeline.
  """
  
  def get(self):
    self.response.write('Start the FolderFetcherPipeline')

