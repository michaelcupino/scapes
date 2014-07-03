import httplib2
import json

from mapreduce import base_handler
from oauth2client.client import OAuth2Credentials
from service import config
from model.revision import Revision

class DocumentRevisionsPipeline(base_handler.PipelineBase):
  """A pipeline that returns a list of revision export links of a document.
  
  Args:
    toEmail: The email address reciever of this message.
    documentId: The document id the document that contains the list of
      revisions.
    credentialsAsJson: A json representation of user's oauth2 credentials.

  Returns:
    List of Revisions of a document.
  """
  
  # TODO(michaelcupino): Remove unused toEmail paramater.
  def run(self, toEmail, documentId, credentialsAsJson):
    credentials = OAuth2Credentials.from_json(credentialsAsJson)
    http = credentials.authorize(httplib2.Http())

    request = config.getService().revisions().list(fileId=documentId)
    response = request.execute(http=http)

    revisions = []
    for item in response.get('items'):
      revision = Revision()
      revision.documentId = documentId
      revision.revisionNumber = item.get('id')
      revision.author = item.get('lastModifyingUserName')
      revision.exportLink = item.get('exportLinks').get('text/plain')
      revision.dateTime = item.get('modifiedDate')
      revisions.append(revision.to_dict())
    return revisions

