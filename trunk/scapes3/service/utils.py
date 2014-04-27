"""Util methods"""
import functools
import google.appengine.ext.cloudstorage as gcs
import pickle
import re

from handler.revision_analyzer_core import revision_text
from handler.revision_core import retrieve_revisions
from google.appengine.ext import blobstore

def split_into_sentences(s):
  """Split text into list of sentences."""
  s = re.sub(r"\s+", " ", s)
  s = re.sub(r"[\\.\\?\\!]", "\n", s)
  return s.split("\n")


def split_into_words(s):
  """Split a sentence into list of words."""
  s = re.sub(r"\W+", " ", s)
  s = re.sub(r"[_0-9]+", " ", s)
  return s.split()

def scapes_write_to_blobstore(filename, contents):
  """Create a GCS file with GCS client lib.

  Args:
    filename: GCS filename.

  Returns:
    The corresponding string blobkey for this GCS file.
  """
  # Create a GCS file with GCS client.
  with gcs.open(filename, 'w') as f:
    f.write(contents)

  # Blobstore API requires extra /gs to distinguish against blobstore files.
  blobstore_filename = '/gs' + filename
  # This blob_key works with blobstore APIs that do not expect a
  # corresponding BlobInfo in datastore.
  return blobstore.create_gs_key(blobstore_filename)
  
  
def scapes_analyse_document(data):
  # recall that ASCII 30 is the record separator
  file_id, http = data.split(chr(30))
  http = pickle.loads(http.replace(chr(31),"\n"),0)
  revisions = retrieve_revisions(http, file_id)
  revision_map = functools.partial(scapes_analyze_revision, http, file_id)
  revisions = map(revision_map, revisions)

  # Postprocess code (Serialization etc.?)
  
  yield revisions

def scapes_analyze_reduce(key, values):
  """Word count reduce function."""
  yield "%s: %d\n" % (key, len(values))
  

def scapes_analyze_revision(http, file_id, rev_id):
    text = revision_text(http, file_id, rev_id)
    for s in split_into_sentences(text):
        for w in split_into_words(s.lower()):
            yield (w, "")

