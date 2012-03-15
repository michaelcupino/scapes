import ConfigParser
import cgi
import csv
import datetime
import difflib
import gdata.docs.client
import gdata.gauth
import jinja2
import os
import string
import time
import urllib
import webapp2
import diff_match_patch.diff_match_patch

from datetime import datetime
from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app, login_required

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


class Revision(db.Model):
  resourceLink = db.StringProperty()
  revisionNumber = db.StringProperty()
  revisionDownloadedText = db.BlobProperty()


class Fetcher(webapp2.RequestHandler):
  @login_required
  def get(self):
    current_user = users.get_current_user()

    scopes = SETTINGS['SCOPES']
    oauth_callback = 'http://%s/step2' % self.request.host
    consumer_key = SETTINGS['CONSUMER_KEY']
    consumer_secret = SETTINGS['CONSUMER_SECRET']
    request_token = gdocs.get_oauth_token(scopes, oauth_callback,
        consumer_key, consumer_secret)

    request_token_key = 'request_token_%s' % current_user.user_id()
    gdata.gauth.ae_save(request_token, request_token_key)

    approvalPageUrl = request_token.generate_authorization_url()

    templateValues = {
      'approvalPageUrl': approvalPageUrl,
    }
    template = jinja_environment.get_template('templates/step1.html')
    self.response.out.write(template.render(templateValues))


class FetchRevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token
    flag = self.request.get('flag')
    uri = self.request.get('uri')

    # TODO(mcupino): AJAXify this
    if uri:
      feed = gdocs.GetResources(uri=uri)
    else:
      feed = gdocs.GetResources(uri='/feeds/default/private/full/-/document')


    documents = []

    if flag == "true":
      for entry in feed.entry:
        resource_id = entry.resource_id.text
        # TODO(mcupino): AJAXify this
        resource = gdocs.GetResourceById(resource_id)
        revisions = gdocs.GetRevisions(resource)
        documentTuple = {
          'entry': entry,
          'flag': "",
        }

        originalAuthor = None
        differentAuthor = False
        flagged = False


        for revision in revisions.entry:
          author = revision.author[0].email.text
          if originalAuthor is None:
            originalAuthor = author
          elif author != originalAuthor:
            differentAuthor = True
          elif differentAuthor and originalAuthor == author:
            #TODO: Move to template values eventually
            documentTuple = {
              'entry': entry,
              'flag': "Interesting",
            }
            flagged = True
            break

        documents.append(documentTuple)
    else:
      resourceLinks = []
      for entry in feed.entry:
        resourceLink = entry.GetSelfLink().href
        resourceLinks.append(resourceLink)
        documentTuple = {
          'entry': entry,
          'flag': "",
        }
        documents.append(documentTuple)

    templateValues = {
      'entries': documents,
      'resourceLinks': resourceLinks
    }
    template = jinja_environment.get_template('templates/step3.html')
    self.response.out.write(template.render(templateValues))


class FetchCollection(webapp2.RequestHandler):
  @login_required
  def get(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    feed = gdocs.GetResources(uri='/feeds/default/private/full/-/folder')

    folders = []
    for entry in feed.entry:
      folder = {
        'title': entry.title.text,
        'id': entry.id.text
      }
      folders.append(folder)

    templateValues = {
      'entries': "",
      'folders': folders
    }
    template = jinja_environment.get_template('templates/collections.html')
    self.response.out.write(template.render(templateValues))

class RequestAResource(webapp2.RequestHandler):
  @login_required
  def get(self):
    #revision = gdocs.GetRevisionBySelfLink(self.request.get('revisionLink'))
    #revisionLink = gdocs.DownloadRevisionToMemory(revision)
    resourceSelfLink = self.request.get('resourceLink')
    allRevisionsQuery = Revision.all()
    revisionsOfResourceQuery = allRevisionsQuery.filter("resourceLink = ",
        resourceSelfLink)

    # TODO: These two lines should only run if it's not stored in the database
    if True:
      resource = gdocs.GetResourceBySelfLink(resourceSelfLink)
      revisions = gdocs.GetRevisions(resource)

    originalAuthor = None
    differentAuthor = False
    flagged = False
    flag = ""

    for revision in revisions.entry:
      revisionLink = revision.GetSelfLink().href
      author = revision.author[0].email.text
      currentRevisionQuery = revisionsOfResourceQuery.filter(
          "revisionNumber =", revisionLink)
      results = currentRevisionQuery.get()
      revisionText = None
      if (results == None):
        revisionText = gdocs.DownloadRevisionToMemory(
            revision, {'exportFormat': 'txt'})
        revisionStore = Revision(resourceLink=resourceSelfLink,
          revisionNumber=revisionLink, revisionDownloadedText=revisionText)
        revisionStore.put()
      else:
        revisionText = results.revisionDownloadedText
      if originalAuthor is None:
        originalAuthor = author
      elif author != originalAuthor:
        differentAuthor = True
      elif differentAuthor and originalAuthor == author:
        flag = "Interesting"
        flagged = True
        break
    templateValues = {
      'resourceLink': self.request.get('resourceLink'),
      'resource': resource,
      'flag': flag
    }
    template = jinja_environment.get_template('templates/requestAResource.html')
    self.response.out.write(template.render(templateValues))


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
    currentRevisionQuery = revisionsOfResourceQuery.filter(
          "revisionNumber = ", revisionSelfLink)
    return currentRevisionQuery.get()

  def getRevisionTextFromQueryResults(self, scapesRevision, revision,
      resourceLink):
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
    if (scapesRevision == None):
      # TODO(someone?): Maybe make this download into a separate function
      # because the client's browser timesout if this takes too long
      revisionText = gdocs.DownloadRevisionToMemory(
          revision, {'exportFormat': 'txt'})
      revisionStore = Revision(resourceLink=resourceLink,
          revisionNumber=revision.GetSelfLink().href,
          revisionDownloadedText=revisionText)
      revisionStore.put()
    else:
      revisionText = scapesRevision.revisionDownloadedText
    return revisionText

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

    resourceSelfLink = resource.GetSelfLink().href
    resourceTitle = resource.title.text
    untypedResourceId = string.lstrip(resourceId, 'document:')

    acl = gdocs.GetResourceAcl(resource)

    previousText = "";
    previousTextUnsplitted = "";
    valuesOfRevisions = []
    originalAuthor = None
    differentAuthor = False
    flagged = False

    allRevisionsQuery = Revision.all()
    revisionsOfResourceQuery = allRevisionsQuery.filter("resourceLink = ",
        resourceSelfLink)

    for revision in revisions.entry:
      scapesRevision = self.getRevisionQueryResults(revision.GetSelfLink().href,
          revisionsOfResourceQuery)
      revisionText = self.getRevisionTextFromQueryResults(scapesRevision,
          revision, resourceSelfLink)
      revisionTextUnsplitted = revisionText
      revisionText = string.split(revisionText, '\n')
      revisionWordCount = self.getWordCount(revisionText)
      revisionTitle = revision.title.text

      # TODO: find out what the Z at the end of the revision.updated means
      lastEditedDateTime = datetime.strptime(revision.updated.text,
          "%Y-%m-%dT%H:%M:%S.%fZ")
      lastEditedDate = lastEditedDateTime.strftime("%a, %m/%d/%y")
      lastEditedTime = lastEditedDateTime.strftime("%I:%M%p")

      newDiffs = gdiff.diff_main(previousTextUnsplitted,
          revisionTextUnsplitted, False)
      gdiff.diff_cleanupSemantic(newDiffs)
      newDiffs = filter(self.isRemoveOrAdd, newDiffs)
      diffWordCount = map(self.countWords, newDiffs)
      addedWordCount = self.getAddWordCount(diffWordCount)
      deletedWordCount = self.getDeletedWordCount(diffWordCount)

      self.response.out.write(newDiffs)
      self.response.out.write(diffWordCount)

      author = revision.author[0].email.text
      if not flagged:
        if originalAuthor is None:
          originalAuthor = author
        elif author != originalAuthor:
          differentAuthor = True
        elif differentAuthor and originalAuthor == author:
          #TODO: Move to template values eventually
          self.response.out.write("Flag as author other author <br />")
          flagged = True

      revisionValues = {
        'author': author,
        'lastEditedDate': lastEditedDate,
        'lastEditedTime': lastEditedTime,
        'revisionTitle': revisionTitle,
        'revisionWordCount': revisionWordCount,
        'addedWordCount': addedWordCount,
        'deletedWordCount': deletedWordCount
      }
      valuesOfRevisions.append(revisionValues)

      previousText = revisionText
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


class RequestARevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    revision = gdocs.GetRevisionBySelfLink(self.request.get('revisionLink'))
    revisionText = gdocs.DownloadRevisionToMemory(
        revision, {'exportFormat': 'txt'})
    revisionText = string.split(revisionText, '\n')
    revisionWordCount = 0
    revisionTitle = revision.title.text

    for line in revisionText:
      line = line.split()
      revisionWordCount = revisionWordCount + len(line)

    currentDiff = ""
    # TODO(dani): Playing with Google API Last Edit
    lastEdit = revision.updated
    linesAdded = 0
    linesDeleted = 0
    linesChanged = 0

    # TODO(mcupino): Find out how to pass on a previous text from each ajax call
    ##for line in difflib.context_diff(previousText, revisionText):
    ##  currentDiff += line
    ##  if line.startswith('+ '):
    ##    linesAdded += 1
    ##  elif line.startswith('- '):
    ##    linesDeleted += 1
    ##  elif line.startswith('! '):
    ##    linesChanged += 1

    author = revision.author[0].email.text
    # TODO(mcupino): Find out how to pass on flaged value from each ajax call
    ##if not flagged:
    ##  if originalAuthor is None:
    ##    originalAuthor = author
    ##  elif author != originalAuthor:
    ##    differentAuthor = True
    ##  elif differentAuthor and originalAuthor == author:
    ##    #TODO: Move to template values eventually
    ##    self.response.out.write("Flag as author other author <br />")
    ##    flagged = True

    # TODO(mcupino): Find out how to pass on a previous text from each ajax call
    # previousText = revisionText

    # TODO(dani): Statistics Summary
    # Lines Added

    templateValues = {
      'revisionLink': self.request.get('revisionLink'),
      'author': author,
      'lastEdit': lastEdit,
      'revisionTitle': revisionTitle,
      'revisionWordCount': revisionWordCount,
      'linesAdded': linesAdded,
      'linesDeleted': linesDeleted,
      'linesChanged': linesChanged
    }
    template = jinja_environment.get_template('templates/requestARevision.html')
    self.response.out.write(template.render(templateValues))


class RequestRawRevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token
    id = self.request.get('id')

    # TODO(jordan): Figure out how to catch exception with invalid resource
    resource = gdocs.GetResourceById(id)
    revisions = gdocs.GetRevisions(resource)

    revisionLinks = []
    for revision in revisions.entry:
      revisionLink = revision.GetSelfLink().href
      revisionLinks.append(revisionLink)

    templateValues = {
      'revisionLinks': revisionLinks,
    }
    template = jinja_environment.get_template('templates/raw.html')
    self.response.out.write(template.render(templateValues))


class RequestARawRevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    revision = gdocs.GetRevisionBySelfLink(self.request.get('revisionLink'))
    revisionLink = gdocs.DownloadRevisionToMemory(revision)
    self.response.out.write(revisionLink)


class RequestTokenCallback(webapp2.RequestHandler):
  @login_required
  def get(self):
    current_user = users.get_current_user()

    # Authorize the request token to be an access token
    request_token_key = 'request_token_%s' % current_user.user_id()
    request_token = gdata.gauth.AeLoad(request_token_key)
    gdata.gauth.authorize_request_token(request_token, self.request.uri)

    # Create the long lived access token from the request token
    gdocs.auth_token = gdocs.get_access_token(request_token)
    access_token = request_token

    # Store the access token
    access_token_key = 'access_token_%s' % current_user.user_id()
    gdata.gauth.ae_save(access_token, access_token_key)

    # TODO(someone?): Find out what webap2.redirect does
    webapp2.redirect('step3')
    template = jinja_environment.get_template('templates/step2.html')
    self.response.out.write(template.render())


class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      template = jinja_environment.get_template('templates/indexUser.html')
      templateValues = {
        'nickname': user.nickname(),
        'logoutLink': users.create_logout_url(self.request.uri),
      }
    else:
      template = jinja_environment.get_template('templates/indexNoUser.html')
      templateValues = {
        'loginLink': users.create_login_url(self.request.uri),
      }
    self.response.out.write(template.render(templateValues))


class GoogleWebmasterVerify(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('google910e6da758dc80f1.html')
    self.response.out.write(template.render())


class CsvPlayground(webapp2.RequestHandler):
  def get(self):
    # TODO: Connect this request with a call to the datastore
    self.response.headers['Content-Type'] = 'text/csv'
    writer = csv.writer(self.response.out)
    values = [[self.request.get('resourceSelfLink'), 'column 2', 'column 3'],
        ['value 1', 'value 2', 'value 3'],
        ['value 4', 'value 5', 'value 6']]
    writer.writerows(values)

# TODO(mcupino): Maybe find out how to have the GoogleWebmasterVerify
# automatically route to the html page?
app = webapp2.WSGIApplication([('/', MainPage),
    ('/google910e6da758dc80f1.html', GoogleWebmasterVerify),
    ('/step1', Fetcher),
    ('/step2', RequestTokenCallback),
    ('/step3', FetchRevision),
    ('/step4', RequestRevision),
    ('/collections', FetchCollection),
    ('/raw', RequestRawRevision),
    ('/requestAResource', RequestAResource),
    ('/requestARawRevision', RequestARawRevision),
    ('/requestARevision', RequestARevision),
    ('/csv-example.csv', CsvPlayground)],
    debug=True)
