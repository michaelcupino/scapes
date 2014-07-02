import httplib2

from mapreduce import base_handler
from mapreduce.lib.pipeline import common
from oauth2client.client import OAuth2Credentials
from service import config

class FolderFetcherPipeline(base_handler.PipelineBase):
  """A pipeline that returns all the Google Doc ids inside the folder plus all
  the Google Doc ids inside subfolders.

  Args:
    folderId: The folder id of the document that contains the list of
      documents and more folders.
    credentialsAsJson: A json representation of user's oauth2 credentials.

  Returns:
    List of documents ids in this folder (recursively).
  """
  
  def run(self, folderId, credentialsAsJson):
    credentials = OAuth2Credentials.from_json(credentialsAsJson)
    http = credentials.authorize(httplib2.Http())


    folderQuery = ('mimeType = "application/vnd.google-apps.folder" and '
        'trashed = false')
    folderListPageToken = None
    deeperDocumentIdsFutures = []
    while True:
      # TODO(michaelcupino): Do this in a try except statement.
      request = config.getService().children().list(
          folderId=folderId,
          pageToken=folderListPageToken,
          maxResults=1000,
          q=folderQuery)
      folderList = request.execute(http=http)

      # Recursively fetch document ids for folders inside the current folder.
      for folder in folderList.get('items'):
        deeperFolderId = folder.get('id')
        deeperDocumentIdsFuture = yield FolderFetcherPipeline(deeperFolderId,
            credentialsAsJson)
        deeperDocumentIdsFutures.append(deeperDocumentIdsFuture)

      folderListPageToken = folderList.get('nextPageToken')
      if not folderListPageToken:
        break

    documentQuery = ('mimeType = "application/vnd.google-apps.document" and '
        'trashed = false')
    docListPageToken = None
    documentIds = []
    while True:
      # TODO(michaelcupino): Do this in a try except statement.
      request = config.getService().children().list(
          folderId=folderId,
          pageToken=docListPageToken,
          maxResults=1000,
          q=documentQuery)
      docList = request.execute(http=http)

      for document in docList.get('items'):
        documentIds.append(document.get('id'))

      docListPageToken = docList.get('nextPageToken')
      if not docListPageToken:
        break

    yield common.Extend(documentIds, *deeperDocumentIdsFutures)

