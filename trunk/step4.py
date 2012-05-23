import ConfigParser
import copy
import diff_match_patch.diff_match_patch
import jinja2
import gdata.gauth
import os
import string
import urllib
import webapp2
from datetime import datetime
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from scapesmodel import Revision

# TODO: Find out if we can have only one reference of this
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Configure gdata
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
SETTINGS = {
  'APP_NAME': config.get('gdata_settings', 'APP_NAME'),
  'CONSUMER_KEY': config.get('gdata_settings', 'CONSUMER_KEY'),
  'CONSUMER_SECRET': config.get('gdata_settings', 'CONSUMER_SECRET'),
  'SCOPES': [config.get('gdata_settings', 'SCOPES')]
}

gdocs = gdata.docs.client.DocsClient(source = SETTINGS['APP_NAME'])
gdiff = diff_match_patch.diff_match_patch()

class RequestRevision(webapp2.RequestHandler):
  """Handles requests to analyze a document."""

  def isRemove(self, x):
    """Determines whether a gdiff tuple signifies a removal. Helps with
    with the filtering.
    """
    return x[0] == gdiff.DIFF_DELETE

  def isAdd(self, x):
    """Determines whether a gdiff tuple signifies an add. Helps with
    with the filtering.
    """
    return x[0] == gdiff.DIFF_INSERT

  def isRemoveOrAdd(self, x):
    """Determines whether a gdiff tuple signifies either an add or a removal.
    Helps with with the filtering.
    """
    return x[0] != gdiff.DIFF_EQUAL

  # TODO(mcupino): Make this into a separate higher level function, so
  # we don't have to do if elses for every time we reduce
  # TODO(mcupino): Don't count characters that were appended to a word
  # as a word added
  def addWordCount(self, x, y):
    """Adds "diff tuples" together. Helps with reducing."""
    if type(x) == type(1):
      return x + y[1]
    else:
      return x[1] + y[1]

  def countWords(self, x):
    """Counts the number of words in a String. Helps with mapping."""
    splitedString = x[1].split()
    wordCount = len(splitedString)
    return (x[0], wordCount)

  def getWordCount(self, revisionText):
    """Counts the number of words in a String

    Args:
     revisionText: String. Text of the revision.

    Returns:
      Int. Number of words in revisionText.
    """
    wordCount = 0;
    for line in revisionText:
      line = line.split()
      wordCount = wordCount + len(line)
    return wordCount

  def getAddWordCount(self, diffWordCount):
    """Returns the word count of "added-diff tuples".

    Args:
      diffWordCount: [(operator, Int)] List of tuples

    Returns:
      Int. Number of words added.
    """
    newDiffsAdded = filter(self.isAdd, diffWordCount)
    if newDiffsAdded == []:
      return 0
    elif len(newDiffsAdded) == 1:
      return newDiffsAdded[0][1]
    else:
      return reduce(self.addWordCount, newDiffsAdded)

  def getDeletedWordCount(self, diffWordCount):
    """Returns the word count of "removed-diff tuples".

    Args:
      diffWordCount: [(operator, Int)] List of tuples

    Returns:
      Int. Number of words removed.
    """
    newDiffsRemoved = filter(self.isRemove, diffWordCount)
    if newDiffsRemoved == []:
      return 0
    elif len(newDiffsRemoved) == 1:
      return newDiffsRemoved[0][1]
    else:
      return reduce(self.addWordCount, newDiffsRemoved)

  def getRevisionQueryResults(self, revisionSelfLink,
      revisionsOfResourceQuery):
    # TODO: Update description and comments
    """Either downloads the reivsion text from the API or reterives the
    the revision from the datastore.

    Args:
      scapesRevision: Revision. This can be None
      revision: gdata.docs.data.revision. The gdata Revision object that
          helps with downloading
      resourceLink: String.

    Returns:
      Revision object
    """
    currentRevisionQuery = revisionsOfResourceQuery.filter(
          "revisionNumber = ", revisionSelfLink)
    if (currentRevisionQuery.count(1) == 0):
      return Revision()
    else:
      return currentRevisionQuery.get()

  def getRevisionTextFromQueryResults(self, scapesRevision, revision,
      resourceLink, resourceID, resourceTitle):
    """Either downloads the reivsion text from the API or reterives the
    the revision from the datastore.

    Args:
      scapesRevision: Revision. This can be None
      revision: gdata.docs.data.revision. The gdata Revision object that
          helps with downloading
      resourceLink: String.

    Returns:
      String that contains the revision text
    """
    revisionText = None
    if (scapesRevision.revisionDownloadedText is None):
      # TODO(someone?): Maybe make this download into a separate function
      # because the client's browser timesout if this takes too long
      revisionText = gdocs.DownloadRevisionToMemory(
          revision, {'exportFormat': 'txt'})
      scapesRevision.resourceLink = resourceLink
      scapesRevision.revisionNumber = revision.GetSelfLink().href
      scapesRevision.revisionDownloadedText = revisionText
      scapesRevision.documentID = resourceID
      scapesRevision.documentName = resourceTitle
      scapesRevision.put()
    else:
      revisionText = scapesRevision.revisionDownloadedText
    return revisionText

  def post(self): # should run at most 1/s
    documentSelfLink = self.request.get('documentSelfLink')
    userId = self.request.get('userId')
    access_token_key = 'access_token_%s' % userId 
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    # TODO(jordan): Figure out how to catch exception with invalid resource
    # TODO: This should only run if it's not in the database
    if True:
      resource = gdocs.GetResourceBySelfLink(documentSelfLink)
      resourceId = resource.resource_id.text
      revisions = gdocs.GetRevisions(resource)

    resourceSelfLink = urllib.unquote(resource.GetSelfLink().href)
    resourceTitle = resource.title.text
    untypedResourceId = string.lstrip(resourceId, 'document:')

    previousTextUnsplitted = "";
    valuesOfRevisions = []
    originalAuthor = None
    differentAuthor = False
    flagged = False

    allRevisionsQuery = Revision.all()
    revisionsOfResourceQuery = allRevisionsQuery.filter("resourceLink = ",
        resourceSelfLink)

    for revision in revisions.entry:
      # TODO: We are doing a deepcopy of the revisionsOfResourceQuery, so
      # it could take up less resources if we either make separte query calls
      # or iterate through the revisionsOfResourceQuery
      scapesRevision = self.getRevisionQueryResults(revision.GetSelfLink().href,
          copy.deepcopy(revisionsOfResourceQuery))
      revisionText = self.getRevisionTextFromQueryResults(scapesRevision,
          revision, resourceSelfLink, untypedResourceId, resourceTitle)
      # self.response.out.write(resourceSelfLink)
      revisionTextUnsplitted = revisionText
      revisionText = string.split(revisionText, '\n')
      revisionWordCount = self.getWordCount(revisionText)
      scapesRevision.wordCount = revisionWordCount
      revisionTitle = revision.title.text

      # TODO: find out what the Z at the end of the revision.updated means
      lastEditedDateTime = datetime.strptime(revision.updated.text,
          "%Y-%m-%dT%H:%M:%S.%fZ")
      lastEditedDateString = lastEditedDateTime.strftime("%a, %m/%d/%y")
      scapesRevision.date = lastEditedDateTime.date()
      lastEditedTimeString = lastEditedDateTime.strftime("%I:%M%p")
      scapesRevision.time = lastEditedDateTime.time()

      newDiffs = gdiff.diff_main(previousTextUnsplitted,
          revisionTextUnsplitted, False)
      gdiff.diff_cleanupSemantic(newDiffs)
      newDiffs = filter(self.isRemoveOrAdd, newDiffs)
      diffWordCount = map(self.countWords, newDiffs)
      addedWordCount = self.getAddWordCount(diffWordCount)
      scapesRevision.wordsAdded = addedWordCount
      deletedWordCount = self.getDeletedWordCount(diffWordCount)
      scapesRevision.wordsDeleted = deletedWordCount

      # self.response.out.write(newDiffs)
      # self.response.out.write(diffWordCount)

      ###########################
      # TODO: We are assuming that there is only one author per revision because
      # the Google Docs API does not return more than one author even though a
      # revision contains more than one author
      #
      # The API could change, and SCAPES is not prepared for a change.
      ###########################
      author = revision.author[0].email.text
      scapesRevision.author = author
      if not flagged:
        if originalAuthor is None:
          originalAuthor = author
        elif author != originalAuthor:
          differentAuthor = True
        elif differentAuthor and originalAuthor == author:
          #TODO: Move to template values eventually
          self.response.out.write("Flag as author other author <br />")
          flagged = True

      scapesRevision.put()
      revisionValues = {
        'author': author,
        'lastEditedDate': lastEditedDateString,
        'lastEditedTime': lastEditedTimeString,
        'revisionTitle': revisionTitle,
        'revisionWordCount': revisionWordCount,
        'addedWordCount': addedWordCount,
        'deletedWordCount': deletedWordCount
      }
      valuesOfRevisions.append(revisionValues)

      previousTextUnsplitted = revisionTextUnsplitted

    templateValues = {
      'valuesOfRevisions': valuesOfRevisions,
      'revisionCount': len(revisions.entry),
      'resourceTitle': resourceTitle,
      'untypedResourceId': untypedResourceId,
      'resourceSelfLink': resourceSelfLink
    }

  @login_required
  def get(self):
    """GET method for the handler. Analyzezs the resource/document."""
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token
    resourceId = self.request.get('id')

    # TODO(jordan): Figure out how to catch exception with invalid resource
    # TODO: This should only run if it's not in the database
    if True:
      resource = gdocs.GetResourceById(resourceId)
      revisions = gdocs.GetRevisions(resource)

    resourceSelfLink = urllib.unquote(resource.GetSelfLink().href)
    resourceTitle = resource.title.text
    untypedResourceId = string.lstrip(resourceId, 'document:')

    previousTextUnsplitted = "";
    valuesOfRevisions = []
    originalAuthor = None
    differentAuthor = False
    flagged = False

    allRevisionsQuery = Revision.all()
    revisionsOfResourceQuery = allRevisionsQuery.filter("resourceLink = ",
        resourceSelfLink)

    for revision in revisions.entry:
      # TODO: We are doing a deepcopy of the revisionsOfResourceQuery, so
      # it could take up less resources if we either make separte query calls
      # or iterate through the revisionsOfResourceQuery
      scapesRevision = self.getRevisionQueryResults(revision.GetSelfLink().href,
          copy.deepcopy(revisionsOfResourceQuery))
      revisionText = self.getRevisionTextFromQueryResults(scapesRevision,
          revision, resourceSelfLink, untypedResourceId, resourceTitle)
      # self.response.out.write(resourceSelfLink)
      revisionTextUnsplitted = revisionText
      revisionText = string.split(revisionText, '\n')
      revisionWordCount = self.getWordCount(revisionText)
      scapesRevision.wordCount = revisionWordCount
      revisionTitle = revision.title.text

      # TODO: find out what the Z at the end of the revision.updated means
      lastEditedDateTime = datetime.strptime(revision.updated.text,
          "%Y-%m-%dT%H:%M:%S.%fZ")
      lastEditedDateString = lastEditedDateTime.strftime("%a, %m/%d/%y")
      scapesRevision.date = lastEditedDateTime.date()
      lastEditedTimeString = lastEditedDateTime.strftime("%I:%M%p")
      scapesRevision.time = lastEditedDateTime.time()

      newDiffs = gdiff.diff_main(previousTextUnsplitted,
          revisionTextUnsplitted, False)
      gdiff.diff_cleanupSemantic(newDiffs)
      newDiffs = filter(self.isRemoveOrAdd, newDiffs)
      diffWordCount = map(self.countWords, newDiffs)
      addedWordCount = self.getAddWordCount(diffWordCount)
      scapesRevision.wordsAdded = addedWordCount
      deletedWordCount = self.getDeletedWordCount(diffWordCount)
      scapesRevision.wordsDeleted = deletedWordCount

      # self.response.out.write(newDiffs)
      # self.response.out.write(diffWordCount)

      ###########################
      # TODO: We are assuming that there is only one author per revision because
      # the Google Docs API does not return more than one author even though a
      # revision contains more than one author
      #
      # The API could change, and SCAPES is not prepared for a change.
      ###########################
      author = revision.author[0].email.text
      scapesRevision.author = author
      if not flagged:
        if originalAuthor is None:
          originalAuthor = author
        elif author != originalAuthor:
          differentAuthor = True
        elif differentAuthor and originalAuthor == author:
          #TODO: Move to template values eventually
          self.response.out.write("Flag as author other author <br />")
          flagged = True

      scapesRevision.put()
      revisionValues = {
        'author': author,
        'lastEditedDate': lastEditedDateString,
        'lastEditedTime': lastEditedTimeString,
        'revisionTitle': revisionTitle,
        'revisionWordCount': revisionWordCount,
        'addedWordCount': addedWordCount,
        'deletedWordCount': deletedWordCount
      }
      valuesOfRevisions.append(revisionValues)

      previousTextUnsplitted = revisionTextUnsplitted

    templateValues = {
      'valuesOfRevisions': valuesOfRevisions,
      'revisionCount': len(revisions.entry),
      'resourceTitle': resourceTitle,
      'untypedResourceId': untypedResourceId,
      'resourceSelfLink': resourceSelfLink
    }
    template = jinja_environment.get_template('templates/step4.html')
    self.response.out.write(template.render(templateValues))
