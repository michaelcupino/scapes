from mapreduce import base_handler
from mapreduce.lib.pipeline import common as pipeline_common
from pipeline.revision_fetcher_pipeline import RevisionFetcherPipeline
from pipeline.revisions_diff_pipeline import RevisionsDiffPipeline

class RevisionsAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline that analyzes two revisions and returns the number of words
  added and number of words deleted.

  Args:
    exportLinks: The export links of a resources that contains the actual text
        in a revision.

  Returns:
    Temporarily return an array with numbers signifying how many characters were
    deleted and added. This will eventually return a dictionary with the
    revision id as the key and a ScapesRevisionAnalysis object as the value.
  """
  
  def run(self, exportLinks):
    revisionTexts = []
    for exportLink in exportLinks:
      revisionText = yield RevisionFetcherPipeline(exportLink)
      revisionTexts.append(revisionText)

    scapesDiffs = []
    for i in range(len(revisionTexts)):
      previousRevisionText = '' if i == 0 else revisionTexts[i - 1]
      currentRevisionText = revisionTexts[i]
      scapesDiff = yield RevisionsDiffPipeline(previousRevisionText,
          currentRevisionText)
      scapesDiffs.append(scapesDiff)

    # TODO(michaelcupino): Return a dictionary with ScapesRevisionAnalysis
    # objects.
    yield pipeline_common.List(*scapesDiffs)

