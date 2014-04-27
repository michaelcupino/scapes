from apiclient import errors, discovery
from google.appengine.ext.webapp.util import login_required
from oauth2client import appengine, client
import os, jinja2, webapp2

from service import config

def retrieve_all_files(http, service = None):
  """Retrieve a list of File resources.

  Args:
    service: Drive API service instance.

  Returns:
  List of File resources.
  """

  service = service or config.service

  result = []
  page_token = None
  while True:
    try:
      param = {}
      if page_token:
        param['pageToken'] = page_token
      files = service.files().list(**param).execute(http=http)

      result.extend(files['items'])
      page_token = files.get('nextPageToken')
      if not page_token:
        break
    except errors.HttpError, error:
      print 'An error occurred: %s' % error
      break
  return result

