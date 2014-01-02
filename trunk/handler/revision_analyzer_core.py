import revision_core
from apiclient import errors
from service import config

def revision_text(http, file_id, rev_id):
  revision = revision_core.revision_details(http, file_id, rev_id)
  ret = http.request(revision["downloadUrl"])
  # for some reason, ret is a tuple when the request
  # succeeds, so try EAFTP
  try:
    return ret[1]
  except KeyError as e:
    raise errors.HttpError(ret.status)

