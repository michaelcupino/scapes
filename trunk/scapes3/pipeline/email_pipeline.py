import csv
import tempfile

from google.appengine.api import mail
from mapreduce import base_handler
from model.revision import Revision

class EmailPipeline(base_handler.PipelineBase):
  """A pipeline that sends an email.
  
  Args:
    toEmail: The email address reciever of this message.
    subject: The subject of this message.
    body: The body of this message.
    documentAnalysis: Analysis.
  """
  
  def run(self, toEmail, subject, body, documentsAnalyses):
    # TODO(michaelcupino): Move csv transforms into a service.
    csvFile = tempfile.TemporaryFile()
    writer = csv.writer(csvFile)
    values = [['Date', 'Time', 'Who in doc', 'Word count', 'Words added',
        'Words deleted', 'Punct. cap', 'Words moved', 'Document ID',
        'Document Name']]
    writer.writerows(values)

    for documentAnalyses in documentsAnalyses:
      for documentAnalysis in documentAnalyses:
        revision = Revision(**documentAnalysis)
        values = [[
          revision.dateTime, # Date
          '', # Time
          revision.author,
          revision.wordCount,
          revision.wordsAdded,
          revision.wordsDeleted,
          '', # Punct. cap
          '', # Words moved
          revision.documentId, # Document ID
          '', # Document Name
        ]]
        writer.writerows(values)

    csvFile.seek(0)
    csvFileBytes = csvFile.read()
    csvFile.close()

    message = mail.EmailMessage()
    message.sender = 'robot@scapes-uci.appspotmail.com'
    message.to = toEmail
    message.subject = subject
    message.body = str(body)
    message.attachments = [('hello.csv', csvFileBytes)]
    message.send()

