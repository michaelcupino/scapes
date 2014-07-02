import json
import webapp2

from google.appengine.api import users
from pipeline.folder_analysis_pipeline import FolderAnalysisPipeline
from service import config

class FolderAnalysisHandler(webapp2.RequestHandler):
  """Handler that starts the FolderAnalysisPipeline.
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
    folderId = requestJson['folderId']
    pipeline = FolderAnalysisPipeline(toEmail, folderId,
        config.decorator.get_credentials().to_json())
    pipeline.start()
    responseJson = {
      'statusMessage': ('Folder analysis has started. List of character '
        'diffs will be sent to %s.' % toEmail),
      'pipelineUrl': pipeline.base_path + '/status?root=' + pipeline.pipeline_id
    }
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(responseJson))

