import httplib2
import json

from mapreduce import base_handler
from mock import patch
from oauth2client.client import OAuth2Credentials
from pipeline.email_pipeline import EmailPipeline
from service import config

class DocumentRevisionsPipeline(base_handler.PipelineBase):
  """A pipeline that logs a list of revision export links of a document.
  
  Args:
    toEmail: The email address reciever of this message.
    documentId: The document id the document that contains the list of
      revisions.
    credentialsAsJson: A json representation of user's oauth2 credentials.
  """
  
  def run(self, toEmail, documentId, credentialsAsJson):
    credentials = OAuth2Credentials.from_json(credentialsAsJson)
    http = credentials.authorize(httplib2.Http())

    request = config.getService().revisions().list(fileId=documentId)
    revisions = request.execute(http)

    exportLinks = []
    for item in revisions.get('items'):
      textExportLink = item.get('exportLinks').get('text/plain')
      exportLinks.append(textExportLink)

    subject = ('SCAPES Robot: Revision export links from document %s' %
        documentId)
    pipeline = EmailPipeline(toEmail, subject,
        json.dumps(exportLinks, indent=2))
    pipeline.start()

