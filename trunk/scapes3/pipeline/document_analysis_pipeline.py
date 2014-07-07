from mapreduce import base_handler
from mapreduce.lib.pipeline import common
from pipeline.document_revisions_pipeline import DocumentRevisionsPipeline
from pipeline.email_pipeline import EmailPipeline
from pipeline.revisions_analysis_pipeline import RevisionsAnalysisPipeline

class DocumentAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline that analyzes a document and returns its analysis.

  Args:
    toEmail: The email address reciever of this message.
    documentId: The document id of the document that will be analyzed.
    credentialsAsJson: A json representation of user's oauth2 credentials.

  Returns:
    Analysis of the document as a list of numbers.
  """
  
  def run(self, toEmail, documentId, credentialsAsJson):
    revisions = yield DocumentRevisionsPipeline(toEmail,
        documentId, credentialsAsJson)
    revisionsAnalysis = yield RevisionsAnalysisPipeline(revisions,
        credentialsAsJson)
    yield common.Return(revisionsAnalysis)

