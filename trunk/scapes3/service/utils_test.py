#!/usr/bin/python

import unittest

from google.appengine.ext import testbed
from service import utils

class UtilsTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def testSplitIntoSentences(self):
    sample_battery = {
      "hahahahahaha" : [
        'hahahahahaha'
      ],
      "!!!a.// }{  //.b??" : [
        '', '', '', 'a', '// }{ //', 'b', '', ''
      ],
      "Well... I'd say!" : [
        'Well', '', '', " I'd say", ''
      ],
      "Hamster Huey, and the Gooey Kablooey" : [
        'Hamster Huey, and the Gooey Kablooey'
      ]
    }
    for key in sample_battery:
      result = utils.split_into_sentences(key)
      expected = sample_battery[key]
      self.assertEqual(result, expected)

  def testSplitIntoWords(self):
    sample_battery = {
      "hahahahahaha" : [
        'hahahahahaha'
      ],
      "Oh, look! A test!" : [
        'Oh', 'look', 'A', 'test'
      ],
      " a  b     c d \t \n r \r d" : [
        'a', 'b', 'c', 'd', 'r', 'd'
      ],
      "a.,b}{c\"dd*d+" : [
        'a', 'b', 'c', 'dd', 'd'
      ]
    }
    for key in sample_battery:
      result = utils.split_into_words(key)
      expected = sample_battery[key]
      self.assertEqual(result, expected)

  def testscapesWriteToBlobstore(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testScapesAnalyseDocument(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testScapesAnalyzeReduce(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

  def testScapesAnalyzeRevision(self):
    # TODO(michaelcupino): Actuall test this
    self.assertEqual(1, 1 + 0)

if __name__ == '__main__':
  unittest.main()

