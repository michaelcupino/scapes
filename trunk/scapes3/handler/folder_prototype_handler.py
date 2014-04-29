import json
import webapp2

from service import config

class FolderPrototypeHandler(webapp2.RequestHandler):
  """Proof of concept handler that gets a list of ids of gdocs inside a folder.
  This does not recursively get ids.
  """
  
  @config.decorator.oauth_aware
  def get(self, folderId):
    # If SCAPES is not allowed to access a user's Google Drive, then the user
    # is asked to give authorization to SCAPES.
    if not config.decorator.has_credentials():
      authUrl = config.decorator.authorize_url()
      self.response.write('<a href=' + authUrl + '>' + authUrl + '</a>')
      return
    
    query = ('mimeType = "application/vnd.google-apps.document" and '
        'trashed = false')
    pageToken = None
    childrenIds = []

    # The Google Drive API returns 100 items max for every response. SCAPES
    # requests for a list of children and makes additional requests if there are
    # more children.
    while True:
      request = config.getService().children().list(
          folderId=folderId,
          q=query,
          pageToken=pageToken)
      children = request.execute(config.decorator.http())

      for item in children.get('items'):
        childrenIds.append(item.get('id'))

      pageToken = children.get('nextPageToken')
      if not pageToken:
        break

    self.response.write(('<pre>' + str(len(childrenIds)) + ' documents</pre>'
        '<pre>' + json.dumps(childrenIds, indent=2) + '</pre>'))

