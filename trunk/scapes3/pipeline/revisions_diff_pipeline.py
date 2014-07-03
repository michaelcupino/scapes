import string

from gdiff import diff_match_patch
from mapreduce import base_handler
from model.revision import Revision

class RevisionsDiffPipeline(base_handler.PipelineBase):
  """A pipeline that calculates the words added and the words removed between
  two texts.

  Args:
    exportLinks: The export links of a resources that contains the actual text
      in a revision.

  Returns:
    Temporarily returns a number that represents how many characters have been
    added or removed. This will eventually return a ScapesDiff object that
    contains how many words were added and removed.
  """
  
  def run(self, revisionTextA, revisionTextB, revisionDict):
    gdiff = diff_match_patch()
    revisionDiffs = gdiff.diff_main(revisionTextA,
        revisionTextB, False)
    gdiff.diff_cleanupSemantic(revisionDiffs)
    revisionDiffs = filter(self.isRemoveOrAdd, revisionDiffs)
    diffWordCount = map(self.countWords, revisionDiffs)
    addedWordCount = self.getAddWordCount(diffWordCount)
    deletedWordCount = self.getDeletedWordCount(diffWordCount)

    revision = Revision(**revisionDict)
    revision.wordsAdded = addedWordCount
    revision.wordsDeleted = deletedWordCount
    revision.wordCount = self.getWordCount(revisionTextB)
    return revision.to_dict()

  def getWordCount(self, revisionText):
    """Counts the number of words in a String

    Args:
     revisionText: String. Text of the revision.

    Returns:
      Int. Number of words in revisionText.
    """

    revisionText = string.split(revisionText, '\n')
    wordCount = 0;
    for line in revisionText:
      line = line.split()
      wordCount = wordCount + len(line)
    return wordCount

  def isRemove(self, x):
    """Determines whether a gdiff tuple signifies a removal. Helps with
    with the filtering.
    """
    return x[0] == diff_match_patch.DIFF_DELETE

  def isAdd(self, x):
    """Determines whether a gdiff tuple signifies an add. Helps with
    with the filtering.
    """
    return x[0] == diff_match_patch.DIFF_INSERT

  def isRemoveOrAdd(self, x):
    """Determines whether a gdiff tuple signifies either an add or a removal.
    Helps with with the filtering.
    """
    return x[0] != diff_match_patch.DIFF_EQUAL

  # TODO(mcupino): Make this into a separate higher level function, so
  # we don't have to do if elses for every time we reduce
  # TODO(mcupino): Don't count characters that were appended to a word
  # as a word added
  def addWordCount(self, x, y):
    """Adds "diff tuples" together. Helps with reducing."""
    if type(x) == type(1):
      return x + y[1]
    else:
      return x[1] + y[1]

  def countWords(self, x):
    """Counts the number of words in a String. Helps with mapping."""
    splitedString = x[1].split()
    wordCount = len(splitedString)
    return (x[0], wordCount)

  def getAddWordCount(self, diffWordCount):
    """Returns the word count of "added-diff tuples".

    Args:
      diffWordCount: [(operator, Int)] List of tuples

    Returns:
      Int. Number of words added.
    """
    newDiffsAdded = filter(self.isAdd, diffWordCount)
    if newDiffsAdded == []:
      return 0
    elif len(newDiffsAdded) == 1:
      return newDiffsAdded[0][1]
    else:
      return reduce(self.addWordCount, newDiffsAdded)

  def getDeletedWordCount(self, diffWordCount):
    """Returns the word count of "removed-diff tuples".

    Args:
      diffWordCount: [(operator, Int)] List of tuples

    Returns:
      Int. Number of words removed.
    """
    newDiffsRemoved = filter(self.isRemove, diffWordCount)
    if newDiffsRemoved == []:
      return 0
    elif len(newDiffsRemoved) == 1:
      return newDiffsRemoved[0][1]
    else:
      return reduce(self.addWordCount, newDiffsRemoved)

