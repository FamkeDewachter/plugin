from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from io import BytesIO
from googleapiclient.http import MediaIoBaseUpload
import os
import mimetypes


def get_folders_hierarchy(service, drive_id):
    """
    Fetches the folder hierarchy of a shared Google Drive
    and organizes it into a nested dictionary structure.

    Args:
        service: The Google Drive service object.
        drive_id: The ID of the shared drive to fetch folders from.
    Returns:
        dict: A dictionary representing folder hierarchy.
    """
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    folders = {}  # Stores all folders by ID
    hierarchy = {}

    page_token = None
    while True:
        results = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                corpora="drive",
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields="nextPageToken, files(id, name, parents)",
                pageToken=page_token,
            )
            .execute()
        )

        for file in results.get("files", []):
            folders[file["id"]] = {
                "id": file["id"],  # Ensure every folder keeps its ID
                "name": file["name"],
                "parents": file.get("parents", []),
                "children": [],  # Prepare a placeholder for child nodes
            }

        page_token = results.get("nextPageToken")
        if not page_token:
            break

    for folder_id, folder_data in folders.items():
        parent_ids = folder_data["parents"]
        if not parent_ids or drive_id in parent_ids:  # It's a root folder
            hierarchy[folder_id] = folder_data
        else:
            for parent_id in parent_ids:
                if parent_id in folders:
                    folders[parent_id]["children"].append(folder_data)

    return hierarchy


def gds_upload_file_shared_drive(
    drive_service, drive_id, file_path, folder_id=None, description=None
):
    """
    Uploads a file to a shared Google Drive.

    Args:
        drive_service: Authenticated Google Drive API service instance.
        drive_id: ID of the shared Google Drive.
        file_path: Path to the file to upload.
        folder_id: ID of the folder in the shared drive where the file will be uploaded.
        description: Description of the file (optional).

    Returns:
        The uploaded file's metadata if successful, None otherwise.
    """
    try:
        # Extract file name from the file path
        file_name = file_path.split("/")[-1]
        mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type:
            mime_type = "application/octet-stream"

        # Create a media file upload object
        media = MediaFileUpload(file_path, resumable=True, mimetype=mime_type)

        # Define file metadata
        file_metadata = {
            "name": file_name,
            "driveId": drive_id,
        }

        # Set the folder ID and description if provided
        if folder_id:
            file_metadata["parents"] = [folder_id]
        if description:
            file_metadata["description"] = description

        # Upload the file
        request = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True,  # Required for shared drives
            fields="id, name",
        )
        response = request.execute()

        print(f"File '{file_name}' uploaded successfully.")
        return response

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def gds_get_files_shared_drive(
    service,
    drive_id,
    search_term=None,
    trashed=False,
    fields="files(id, name)",
):
    """
    Retrieve files from a shared Google Drive based on search criteria,
    excluding folders and shortcuts.

    :param service: Authenticated Google Drive API service instance.
    :param drive_id: ID of the shared drive.
    :param search_term: Optional search term to filter files by name.
    :param trashed: Boolean to include or exclude trashed files.
    :param fields: Fields to include in the response.
    :return: List of files matching the criteria.
    """
    query = (
        f"trashed={str(trashed).lower()} "
        f"and mimeType != 'application/vnd.google-apps.folder' "
        f"and mimeType != 'application/vnd.google-apps.shortcut'"
    )
    if search_term:
        query += f" and name contains '{search_term}'"

    results = (
        service.files()
        .list(
            q=query,
            corpora="drive",
            driveId=drive_id,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields=fields,
        )
        .execute()
    )

    files = results.get("files", [])
    return files


# models/drive_model.py
class DriveModel:
    def __init__(self, drive_service):
        self.drive_service = drive_service

    def get_drives(self):
        """Fetch the list of shared drives."""
        try:
            results = self.drive_service.drives().list().execute()
            shared_drives = results.get("drives", [])

            if not shared_drives:
                print("No shared drives found.")
                return None

            return shared_drives

        except Exception as error:
            print(f"An error occurred: {error}")

    def drive_exists(self, drive_id):
        """Check if a specific drive exists and is accessible."""
        try:
            # Attempt to fetch the drive details
            self.drive_service.drives().get(driveId=drive_id).execute()
            return True
        except Exception as e:
            # If an error occurs, the drive does not exist or is inaccessible
            print(f"Error checking drive existence: {e}")
            return False


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
    :return: Dictionary with folder details (name, id, mimeType, etc.),
        or None if not found.
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


def gds_get_version_info(
    service,
    file_id,
    version_id,
    fields="id,originalFilename",
):
    """
    Get a specific version of a file from Google Drive.

    :param service: Authenticated Google Drive API service instance.
    :param file_id: ID of the file to retrieve the version for.
    :param version_id: ID of the version to retrieve.
    :param fields: Fields to include in the response.

    :return: A dictionary containing version metadata or None if not found.
    """
    try:
        revision = (
            service.revisions()  # Use revisions() instead of files()
            .get(fileId=file_id, revisionId=version_id, fields=fields)
            .execute()
        )

        return revision

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def gds_revert_version(service, file_id, revision_id):

    # Step 1: Set the path to the Downloads folder
    download_folder = os.path.expanduser("~/Downloads")
    file_path = os.path.join(download_folder, "temp_downloaded_file")

    try:
        # Step 2: Download the specific revision
        request = service.revisions().get_media(
            fileId=file_id, revisionId=revision_id
        )
        file_to_download = request.execute()

        with open(file_path, "wb") as temp_file:
            temp_file.write(file_to_download)
        print(f"File downloaded to {file_path}")

    except Exception as error:
        print(f"An error occurred while downloading the file: {error}")
        return

    try:
        # Step 3: Upload the downloaded file as the current version
        with open(file_path, "rb") as f:
            file_data = BytesIO(f.read())

        media_body = MediaIoBaseUpload(
            file_data, mimetype="application/octet-stream", resumable=True
        )
        service.files().update(fileId=file_id, media_body=media_body).execute()
        print("Revision successfully reverted")
    except Exception as error:
        print(f"An error occurred while uploading the file: {error}")

    try:
        os.remove(file_path)
        print(f"File {file_path} deleted.")
    except Exception as error:
        print(f"An error occurred while deleting the file: {error}")


def gds_get_current_version(
    service, file_id, fields="revisions(id, originalFilename)"
):
    """
    Get the most recent version of a file
    given its file_id using Google Drive API.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to retrieve the latest version for.

    :return: The latest revision dictionary or None if no revisions found.

    """
    print(f"Fetching current version for file with ID: {file_id}")
    try:
        revisions = (
            service.revisions()
            .list(
                fileId=file_id,
                fields=fields,
            )
            .execute()
        )

        if not revisions:
            print("No revisions found for file with ID: {file_id}")
            return None

        return revisions["revisions"][-1]

    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def gds_get_versions_of_file(service, file_id):
    """
    List all versions of a file given its file_id,
    sorting them by modified time (most recent first) using Google Drive API.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to list versions for.

    Returns:
        A list of dictionaries containing revision details,
        including the original file name, sorted by modified time.
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


def upload_version_keeping_gd_filename(service, file_id, file_path):
    """
    Uploads a new version of an existing file in
    Google Drive while storing the original filename in appProperties.
    """
    try:
        # Extract local filename
        local_filename = os.path.basename(file_path)

        # Create a MediaFileUpload object
        media = MediaFileUpload(file_path, resumable=True)

        # Prepare metadata with the local filename stored in appProperties
        file_metadata = {
            "appProperties": {"original_filename": local_filename}
        }

        # Update the file with the new version
        updated_file = (
            service.files()
            .update(
                fileId=file_id,
                media_body=media,
                body=file_metadata,
                fields="id, appProperties",
            )
            .execute()
        )

        print(f"File updated successfully with ID: {updated_file.get('id')}")
        print(
            f"Original filename stored: "
            f"{updated_file.get('appProperties', {}).get('original_filename')}"
        )
        return updated_file.get("id")

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def gds_upload_new_version(service, file_id, file_name, file_path):
    """
    Uploads a new version of an existing file in Google Drive.

    Args:
        service: The authenticated Google Drive service object.
        file_id: The ID of the file to upload a new version for.
        file_name: The name of the file to upload.
        file_path: The local path to the new version of the file.

    Returns:
        The updated file's metadata or None if an error occurs.
    """
    # google api uploading versions doesnt allow to store the original
    # filename of the file you want to upload, but instea looks at the
    # name of the file in google drive and sets that as the name of the version
    # so we need to change the name of the file in google drive before upload
    # and revert it back after upload

    try:
        # store original name of the file on google drive

        # change name on google drive
        name_version = os.path.basename(file_path)
        gds_rename_file(service, file_id, name_version)

        # upload new version
        media = MediaFileUpload(file_path, resumable=True)

        updated_file = (
            service.files()
            .update(fileId=file_id, media_body=media, fields="id, name, size")
            .execute()
        )

        # revert name on google drive
        gds_rename_file(service, file_id, file_name)

        print(
            f"New version {name_version} uploaded successfully for file ID: "
            f"{file_id}"
        )
        return updated_file

    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def gds_rename_file(service, file_id, new_name):
    """
    Rename a file in Google Drive.

    :param service: Authenticated Google Drive API service instance.
    :param file_id: ID of the file to rename.
    :param new_name: New name for the file.
    :return: Updated file metadata if successful, None otherwise.
    """
    try:
        # Prepare the update request
        file_metadata = {"name": new_name}

        # Execute the request
        updated_file = (
            service.files()
            .update(fileId=file_id, body=file_metadata, fields="id, name")
            .execute()
        )
        return updated_file

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def test_get_file_info(service, file_id, fields="appProperties, mimeType"):
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
        # Get file content
        request = service.files().get_media(fileId=file_id)
        file_content = request.execute()

        file_metadata = (
            service.files().get(fileId=file_id, fields=fields).execute()
        )

        mime_type = file_metadata.get("mimeType", "text/plain")
        original_filename = file_metadata.get("appProperties", {}).get(
            "original_filename", "Unknown"
        )

        print(
            f"File content fetched successfully. MIME type: {mime_type}, "
            f"Original Filename: {original_filename}"
        )

        return file_content, mime_type, original_filename
    except Exception as error:
        print(f"An error occurred: {error}")
        return b"Failed to fetch file content.", "text/plain"


def gds_get_file_info(service, file_id, fields="id, name, size, mimeType"):
    """
    Fetches information about a file given its ID.

    :param service: Authenticated Google Drive API service instance.
    :param file_id: ID of the file to fetch information for.
    :param fields: Fields to include in the response.

    :return: A dictionary containing file metadata or None if not found.
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
