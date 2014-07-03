#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from pipeline.email_pipeline import EmailPipeline

class EmailPipelineTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_mail_stub()
    self.mailStub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

  def tearDown(self):
    self.testbed.deactivate()

  # TODO(michaelcupino): Find out how to test for attachments?
  def testRun(self):
    pipeline = EmailPipeline('test@example.com')
    pipeline.run('test@example.com', 'Hello from SCAPES', ('This message was '
        'sent from the EmailPipeline map reduce job.'))

    messages = self.mailStub.get_sent_messages(to='test@example.com')
    self.assertEqual(1, len(messages))
    self.assertEqual('robot@scapes-uci.appspotmail.com', messages[0].sender)
    self.assertEqual('Hello from SCAPES', messages[0].subject)
    self.assertEqual(('This message was sent from the EmailPipeline map reduce '
        'job.'), messages[0].body.decode())

if __name__ == '__main__':
  unittest.main()

