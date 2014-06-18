import webapp2
import jinja2


class LayoutHandler(webapp2.RequestHandler):
  """Handler that bootstraps the scapes angularjs app.
  """

  template_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
      autoescape=True)
  
  def get(self):
    self.response.out.write(
        self.template_env.get_template("layout.html").render())

