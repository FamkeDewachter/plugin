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


def list_file_versions(service, file_id):
    """List all versions of a file given its file_id."""
    try:
        # Call the Drive API to list revisions
        revisions = service.revisions().list(fileId=file_id).execute()

        # Check if the file has revisions
        if "revisions" in revisions:
            for revision in revisions["revisions"]:
                print(f"Revision ID: {revision['id']}")
                print(f"Modified Time: {revision['modifiedTime']}")
                print(
                    f"Description: {revision.get('description', 'No description')}"
                )
                print(
                    f"MD5Checksum: {revision.get('md5Checksum', 'No checksum')}"
                )
                print("-" * 40)
        else:
            print("No revisions found for this file.")
    except Exception as error:
        print(f"An error occurred: {error}")
