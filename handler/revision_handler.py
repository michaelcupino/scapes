import pprint
import random
import webapp2
from service import config
import file_core
import revision_core
from google.appengine.api import urlfetch

class RevisionHandler(webapp2.RequestHandler):
  """The RevisionHandler handles revision requests and gives a response with a
  list of revisions for a specific document.
  """

  @config.decorator.oauth_required
  def get(self):
    """Gets the list of revisions"""

    http = config.decorator.http()
    variables = {
      'url': config.decorator.authorize_url(),
      'has_credentials': config.decorator.has_credentials()
    }

    master_id = file_core.retrieve_all_files(http)
    
    error = True
    while error:
      try:
        file_id = random.choice(master_id)['id']
        # file_id = file_id[0]['id']
        num = len(file_id)
        revision = revision_core.retrieve_revisions(http, file_id)[0]["id"]
        import revision_analyzer_core as s_revad
        text = s_revad.revision_text(http, file_id, revision)
        
        try:
          if text.status != "200":
            error=False
        except AttributeError as e:
          print e
          error=False
          
      except TypeError as e:
        print "="*80
        print e
        print "="*80
        
      # except KeyError as e:
      #   print "="*80
      #   print e
      #   print "="*80

    self.response.write("<h1>" + str(num) + " Documents!</h1><br>\
        "+str(len(text.split(" ")))+"<pre>" + str(text[:1000]) + "</pre>")
