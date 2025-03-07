def list_files(service):
    """
    Lists the first 10 files in the user's Google Drive.
    """
    results = (
        service.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    return results.get("files", [])
