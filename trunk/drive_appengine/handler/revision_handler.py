import webapp2

class RevisionHandler(webapp2.RequestHandler):
  """The RevisionHandler handles revision requests and gives a response with a
  list of revisions for a specific document.
  """

  def get(self):
    """Gets the list of revisions"""
    # TODO(PythonNut): Write the list of revisions in the response.

    self.response.write('This is the output of the revision handler.')
