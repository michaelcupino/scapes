import webapp2

class DocumentAnalysisHandler(webapp2.RequestHandler):
  """Handler that starts the DocumentAnalysisPipeline.
  """
  
  def get(self):
    self.response.write('Start the DocumentAnalysisPipeline')

