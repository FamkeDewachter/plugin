from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import mimetypes


def get_most_recent_files(service):
    """
    Lists the 10 most recently modified files in the user's Google Drive.

    Args:
        service: The Google Drive service object.

    Returns:
        A list of file dictionaries with 'id', 'name', and 'modifiedTime' keys.
    """
    print("Fetching most recent files...")

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


def get_folder_by_id(drive_service, folder_id):
    """
    Retrieves the details of a folder in Google Drive using its ID.

    :param drive_service: Authenticated Google Drive service instance.
    :param folder_id: The ID of the folder to look for.
    :return: Dictionary with folder details (name, id, mimeType, etc.), or None if not found.
    """
    print(f"Fetching folder with ID: {folder_id}...")

    try:
        folder = (
            drive_service.files()
            .get(fileId=folder_id, fields="id, name, mimeType, parents")
            .execute()
        )

        # Ensure it's a folder
        if folder["mimeType"] == "application/vnd.google-apps.folder":
            return folder
        else:
            print("The provided ID does not belong to a folder.")
            return None
    except HttpError as e:
        if e.resp.status == 404:
            print("Folder not found.")
        else:
            print(f"An error occurred: {e}")
        return None


def get_folders_hierarchy(service):
    """
    Fetches all folders from Google Drive with the correct hierarchy.

    Returns:
        dict: A dictionary representing folder hierarchy.
    """
    print("Fetching folder hierarchy...")

    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    folders = {}  # Stores all folders by ID
    root_folders = {}  # Stores the final hierarchy

    # Fetch folder list
    results = (
        service.files()
        .list(q=query, fields="files(id, name, parents)")
        .execute()
    )
    items = results.get("files", [])

    # First pass: Store folder metadata
    for item in items:
        folder_id = item["id"]
        folder_name = item["name"]
        parent_id = item.get("parents", ["root"])[
            0
        ]  # Default to "root" if no parent

        folders[folder_id] = {
            "id": folder_id,
            "name": folder_name,
            "parent": parent_id,
            "children": [],
        }

    # Second pass: Build hierarchy safely
    for folder_id, folder_data in folders.items():
        parent_id = folder_data["parent"]
        if parent_id in folders:
            folders[parent_id]["children"].append(folder_data)
        else:
            # Parent folder not found, assign to root
            print(
                f"Warning: Parent ID {parent_id} not found for folder {folder_data['name']}. Assigning to root."
            )
            root_folders[folder_id] = folder_data

    return root_folders


def upload_file(service, file_path, folder_id=None):
    """
    Uploads a file to Google Drive.

    Args:
        service: The Google Drive service object.
        file_path: The path to the file to upload.
        folder_id: The ID of the folder to upload the file to. If None, the file is uploaded to the root folder.

    Returns:
        The ID of the uploaded file, or None if the upload fails.
    """
    print("Uploading file to Google Drive...")

    try:
        file_name = file_path.split("/")[-1]
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type is None:
            mime_type = "application/octet-stream"

        media = MediaFileUpload(file_path, resumable=True, mimetype=mime_type)

        file_metadata = {
            "name": file_name,
        }

        if folder_id:
            file_metadata["parents"] = [folder_id]

        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        print(
            f"File '{file_name}' uploaded successfully with ID: {file.get('id')}"
        )
        return file.get("id")

    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def gds_get_files(service, search_term=None, mime_type=None, trashed=False):
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
    print("Fetching files...")

    query_parts = []

    if search_term:
        query_parts.append(f"name contains '{search_term}'")
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")
    query_parts.append(f"trashed = {str(trashed).lower()}")
    query_parts.append("mimeType != 'application/vnd.google-apps.folder'")
    query_parts.append("mimeType != 'application/vnd.google-apps.shortcut'")

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


def gds_get_versions_of_file(service, file_id):
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
    print(f"Fetching revisions for file with ID: {file_id}")

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


def gds_upload_version(service, file_id, file_path):
    """
    Uploads a new version of a file to Google Drive.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to upload a new version for.
        file_path: The path to the new file to upload.
    """
    print("Uploading new version to Google Drive...")

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


def gds_get_latest_version_id(service, file_id):
    """
    Retrieves the version ID of the latest revision of a file.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to get the latest version for.

    Returns:
        The version ID of the latest revision, or None if an error occurs.
    """
    print("Fetching ID of the latest version of the file...")

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
    print("Fetching file content for file with ID: {file_id}")

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


def gds_get_file_info(service, file_id, fields="id, name, size, mimeType"):
    """
    Fetches information about a file given its ID.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to fetch information for.
        fields: The fields to include in the response. Defaults to 'id, name, mimeType'.

    Returns:
        A dictionary containing information about the file.
    """
    print("Fetching file info for file with ID: {file_id}")

    try:
        file_info = (
            service.files().get(fileId=file_id, fields=fields).execute()
        )
        print(f"File info fetched successfully: {file_info}")
        return file_info
    except Exception as error:
        print(f"An error occurred: {error}")
        return None
