import logging
import urllib2
import httplib2

from mapreduce import base_handler
from mapreduce.lib.pipeline import pipeline
from oauth2client.client import OAuth2Credentials
from service import config

class RevisionFetcherPipeline(base_handler.PipelineBase):
  """A pipeline that fetches the revision text from a web resource.

  Args:
    exportLink: The export link of one resource that contains the actual text
      in a revision.

  Returns:
    The actual text in a revision.
  """
  
  def run(self, exportLink, credentialsAsJson):
    credentials = OAuth2Credentials.from_json(credentialsAsJson)
    http = credentials.authorize(httplib2.Http())
    response = http.request(exportLink)

    if response[0].status == 200:
      return response[1]
    else: 
      raise pipeline.Abort(('There was an error requesting exportLink %s' %
          exportLink))

