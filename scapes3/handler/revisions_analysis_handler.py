import webapp2

class RevisionsAnalysisHandler(webapp2.RequestHandler):
  """Handler that starts the RevisionsAnalysisPipeline.
  """
  
  def get(self):
    self.response.write('Start the RevisionsAnalysisPipeline')

