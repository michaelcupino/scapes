import webapp2

class FolderAnalysisHandler(webapp2.RequestHandler):
  """Handler that starts the FolderAnalysisPipeline.
  """
  
  def get(self):
    self.response.write('Start the FolderAnalysisPipeline')

