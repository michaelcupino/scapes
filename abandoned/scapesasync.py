import webapp2
import logging
import time

from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp

class Counter(db.Model):
    count = db.IntegerProperty(indexed=False)

class CounterWorker(webapp.RequestHandler):
  def post(self): # should run at most 1/s
    logging.getLogger().setLevel(logging.DEBUG)
    key = self.request.get('key')
    def txn():
      counter = Counter.get_by_key_name(key)
      if counter is None:
        counter = Counter(key_name=key, count=1)
      else:
        counter.count += 1
      counter.put()
      logging.debug("CounterWorker: Before sleeping")
      time.sleep(5)
      logging.debug("CounterWorker: After sleeping")
    db.run_in_transaction(txn)

class AsyncExampleRequestHandler(webapp2.RequestHandler):
  def get(self):
    logging.getLogger().setLevel(logging.DEBUG)
    self.response.out.write('hello')
    key = 5
    
    # Add the task to the default queue.
    logging.debug("AsyncExample: Before making the async call")
    taskqueue.add(url='/worker', params={'key': key})
    logging.debug("AsyncExample: After making the async call")
