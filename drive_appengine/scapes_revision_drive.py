from apiclient import errors

# from the Google API reference
def retrieve_revisions(service, file_id):
    """Retrieve a list of revisions.
    Args:
      service: Drive API service instance.
      file_id: ID of the file to retrieve revisions for.
    Returns:
      List of revisions.
    """
    try:
        revisions = service.revisions().list(fileId=file_id).execute()
        return revisions.get('items', [])
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None

# also from the Google reference
def print_revision(service, file_id, revision_id):
    """Print information about the specified revision.
    Args:
    service: Drive API service instance.
      file_id: ID of the file to print revision for.
      revision_id: ID of the revision to print.

    """
    try:
        revision = service.revisions().get(
            fileId=file_id, revisionId=revision_id).execute()

        return (
            revision['id'],
            revision['modifiedDate'],
            revision.get('pinned')
        )
    except errors.HttpError, err:
        print 'An error occurred: %s' % err

