from mapreduce import base_handler
from mapreduce.lib.pipeline import common
from oauth2client.client import OAuth2Credentials
from pipeline.folder_fetcher_pipeline import FolderFetcherPipeline

class FolderAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline that analyzes a folder and emails its analysis to the requester.

  Args:
    toEmail: The email address reciever of this message.
    documentId: The folder id of the folder that will be analyzed.
    credentialsAsJson: A json representation of user's oauth2 credentials.

  Returns:
    Analyses of documents in the folder.
  """
  
  def run(self, toEmail, folderId, credentialsAsJson):
    documentIds = yield FolderFetcherPipeline(folderId, credentialsAsJson)
    yield common.Log.info(('An email would be sent to %s. These are the '
        'document ids inside folder %s: %s'), toEmail, folderId, documentIds)

