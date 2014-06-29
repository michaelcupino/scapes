import json
import webapp2

class AngularHandler(webapp2.RequestHandler):
  """This handler acts just as an example for client and server side
  communication. This will be deleted.
  """

  def post(self):
    dictionary = {
      'statusMessage': 'Hello from the server.',
      'numberOfDocs': 4
    }
    self.response.out.write(json.dumps(dictionary))

