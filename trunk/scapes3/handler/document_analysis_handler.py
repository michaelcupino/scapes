import json
import webapp2

from google.appengine.api import users
from pipeline.document_analysis_pipeline import DocumentAnalysisPipeline
from service import config

class DocumentAnalysisHandler(webapp2.RequestHandler):
  """Handler that starts the DocumentAnalysisPipeline.
  """
  
  @config.decorator.oauth_aware
  def post(self):
    if not config.decorator.has_credentials():
      responseJson = {
        'statusMessage': 'SCAPES is not authorized to access your Google Docs.',
        'authUrl': '/authredirect'
      }
      self.response.out.write(json.dumps(responseJson))
      return

    toEmail = users.get_current_user().email()
    requestJson = json.loads(self.request.body)
    documentId = requestJson['docId']
    pipeline = DocumentAnalysisPipeline(toEmail, documentId,
        config.decorator.get_credentials().to_json())
    pipeline.start()
    responseJson = {
      'statusMessage': ('Document analysis has started. List of character '
        'diffs will be sent to %s.' % toEmail),
      'pipelineUrl': pipeline.base_path + '/status?root=' + pipeline.pipeline_id
    }
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(responseJson))

