import httplib2
import json

from mapreduce import base_handler
from oauth2client.client import OAuth2Credentials
from service import config

class DocumentRevisionsPipeline(base_handler.PipelineBase):
  """A pipeline that returns a list of revision export links of a document.
  
  Args:
    toEmail: The email address reciever of this message.
    documentId: The document id the document that contains the list of
      revisions.
    credentialsAsJson: A json representation of user's oauth2 credentials.

  Returns:
    List of revision export links of a document.
  """
  
  # TODO(michaelcupino): Remove unused toEmail paramater.
  def run(self, toEmail, documentId, credentialsAsJson):
    credentials = OAuth2Credentials.from_json(credentialsAsJson)
    http = credentials.authorize(httplib2.Http())

    request = config.getService().revisions().list(fileId=documentId)
    revisions = request.execute(http=http)

    exportLinks = []
    for item in revisions.get('items'):
      textExportLink = item.get('exportLinks').get('text/plain')
      exportLinks.append(textExportLink)
    return exportLinks

