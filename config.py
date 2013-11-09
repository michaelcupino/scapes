"""This is the place to put your global variables, or Module level singletons.
For more information, see docs.python.org/2/faq/programming#how-do-i-share-global-variables-across-modules"""

# this is the jinja2.Environment global
import jinja2, os
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
