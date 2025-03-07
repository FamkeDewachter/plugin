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


def map_file_ids(files):
    """
    Maps file names to their IDs.

    Args:
        files: List of file dictionaries with 'id' and 'name' keys.

    Returns:
        A dictionary mapping file names to their IDs.
    """
    return {file["name"]: file["id"] for file in files}
