from googleapiclient.http import MediaFileUpload
from models.auth import authenticate_google_drive
import mimetypes


def get_most_recent_files(service):
    """
    Lists the 10 most recently modified files in the user's Google Drive.

    Args:
        service: The Google Drive service object.

    Returns:
        A list of file dictionaries with 'id', 'name', and 'modifiedTime' keys.
    """
    query = (
        "mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    )

    results = (
        service.files()
        .list(
            q=query,
            pageSize=10,
            fields="files(id, name)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )
    print("Most recent files fetched: ", results)
    return results.get("files", [])


def get_files(service, search_term=None, mime_type=None, trashed=False):
    """
    Searches for files in Google Drive based on provided parameters.

    Args:
        service: The Google Drive service object.
        search_term (str, optional):
        The name or part of the file name to search.
        mime_type (str, optional): The MIME type of the files to search.
        trashed (bool, optional):
        Whether to include trashed files in the search. Defaults to False.

    Returns:
        A list of file dictionaries with 'id' and 'name' keys.
    """
    query_parts = []

    if search_term:
        query_parts.append(f"name contains '{search_term}'")
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")
    query_parts.append(f"trashed = {str(trashed).lower()}")

    query = " and ".join(query_parts)

    results = (
        service.files()
        .list(
            q=query,
            pageSize=20,
            fields="files(id, name)",
        )
        .execute()
    )
    print("Files fetched: ", results)
    return results.get("files", [])


def get_versions_of_file(service, file_id):
    """
    List all versions of a file given its file_id,
      including the original file name of each version.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to list versions for.

    Returns:
        A list of dictionaries containing revision details,
          including the original file name.
    """
    try:
        revisions = (
            service.revisions()
            .list(
                fileId=file_id,
                fields="revisions(id, modifiedTime, originalFilename)",
            )
            .execute()
        )

        # Check if the file has revisions
        if "revisions" in revisions:
            print(
                "Revisions of file with ID: ",
                file_id + " fetched successfully.",
            )
            return revisions["revisions"]
        else:
            return None
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def upload_version(service, file_id, file_path):
    """
    Uploads a new version of a file to Google Drive.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to upload a new version for.
        file_path: The path to the new file to upload.
    """
    try:
        file_name = file_path.split("/")[-1]
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type is None:
            mime_type = "application/octet-stream"

        media = MediaFileUpload(file_path, resumable=True, mimetype=mime_type)

        # Upload the new version to Google Drive

        service.files().update(
            fileId=file_id,
            media_body=media,
            body={
                "name": file_name,
            },
            fields="id",
        ).execute()

        print("New version uploaded successfully.")
        return True

    except Exception as error:
        print(f"An error occurred: {error}")
        return False


def get_latest_version_id(service, file_id):
    """
    Retrieves the version ID of the latest revision of a file.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to get the latest version for.

    Returns:
        The version ID of the latest revision, or None if an error occurs.
    """
    try:
        # Get the list of revisions (versions) for the file
        revisions = service.revisions().list(fileId=file_id).execute()

        # The last revision in the list is the most recent version
        latest_revision = revisions["revisions"][-1]

        # Return the version ID of the latest revision
        return latest_revision["id"]

    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def get_file_content(service, file_id):
    """
    Fetches the content of a file given its ID.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to fetch content for.

    Returns:
        A tuple containing the content of the file and its MIME type.
    """
    try:
        request = service.files().get_media(fileId=file_id)
        file_content = request.execute()
        file_metadata = (
            service.files().get(fileId=file_id, fields="mimeType").execute()
        )
        mime_type = file_metadata.get("mimeType", "text/plain")
        print(f"File content fetched successfully. MIME type: {mime_type}")
        return file_content, mime_type
    except Exception as error:
        print(f"An error occurred: {error}")
        return b"Failed to fetch file content.", "text/plain"


def get_file_info(service, file_id, fields="id, name, size, mimeType"):
    """
    Fetches information about a file given its ID.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to fetch information for.
        fields: The fields to include in the response. Defaults to 'id, name, mimeType'.

    Returns:
        A dictionary containing information about the file.
    """
    try:
        file_info = (
            service.files().get(fileId=file_id, fields=fields).execute()
        )
        print(f"File info fetched successfully: {file_info}")
        return file_info
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


if __name__ == "__main__":
    service = authenticate_google_drive()
    latest_id = get_current_version_id(
        service, "1nRFbLSWWW3h5pxBAEBJoCVL6jjNPLBro"
    )
    print(latest_id)
