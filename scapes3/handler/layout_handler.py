import jinja2
import json
import webapp2

from google.appengine.api import users

class LayoutHandler(webapp2.RequestHandler):
  """Handler that bootstraps the scapes angularjs app.
  """

  template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),
      autoescape=True)
  
  def get(self):
    # Please keep this in sync with scapesexterns.ScapesConfig in externs.js
    scapesConfig = {
      'isUserLoggedIn': bool(users.get_current_user()),
      'loginUrl': users.create_login_url(),
    }
    templateValues = {
      'scapesConfig': json.dumps(scapesConfig),
    }
    template = self.template_env.get_template('layout.html')
    self.response.out.write(template.render(templateValues))

