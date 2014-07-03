from mapreduce import base_handler
from mapreduce.lib.pipeline import common
from oauth2client.client import OAuth2Credentials
from pipeline.folder_fetcher_pipeline import FolderFetcherPipeline
from pipeline.document_analysis_pipeline import DocumentAnalysisPipeline

class DocumentsAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline that analyzes a list of documents.

  Args:
    documentIds: The list documents ids of documents that will be analyzed.
    credentialsAsJson: A json representation of user's oauth2 credentials.

  Returns:
    Analyses of documents in the folder.
  """
  
  def run(self, documentIds, credentialsAsJson):
    analyses = []
    for documentId in documentIds:
      analysis = yield DocumentAnalysisPipeline('hello@example.com', documentId,
          credentialsAsJson)
      analyses.append(analysis)
 
    yield common.List(*analyses)
