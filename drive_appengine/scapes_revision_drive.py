from apiclient import errors

import config

# from the Google API reference
def retrieve_revisions(file_id, service = None, http = None):
    """Retrieve a list of revisions.
    Args:
      service: Drive API service instance.
    file_id: ID of the file to retrieve revisions for.
    Returns:
      List of revisions.
    """

    http    = http    or config.http
    service = service or config.service

    try:
        revisions = service.revisions().list(fileId=file_id)
        revisions = revisions.execute(http=http)
        return revisions.get('items', [])
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None

# also from the Google reference
def print_revision(file_id, revision_id, service = None, http = None):
    """Print information about the specified revision.
    Args:
    service: Drive API service instance.
      file_id: ID of the file to print revision for.
      revision_id: ID of the revision to print.

    """

    http    = http    or config.http
    service = service or config.service

    try:
        revision = service.revisions().get(fileId=file_id, revisionId=revision_id)
        revision = revision.execute(http=http)

        return (
            revision['id'],
            revision['modifiedDate'],
            revision.get('pinned')
        )
    except errors.HttpError, err:
        print 'An error occurred: %s' % err

