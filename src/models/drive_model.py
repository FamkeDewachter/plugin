from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import os
import mimetypes
from utils.drive_utils import gds_rename_file


def gds_get_current_version(
    service, file_id, fields="revisions(id, originalFilename)"
):
    """
    Get the most recent version of a file
    given its file_id using Google Drive API.

    :param service: Authenticated Google Drive API service instance.
    :param file_id: The ID of the file to retrieve the latest version for.
    :param fields: The fields to include in the response.
                     Default is "revisions(id, originalFilename)".

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


def gds_get_versions_of_file_shared_drive(
    service, file_id, fields="id, modifiedTime, originalFilename"
):
    """
    Retrieves the versions of a file from a shared Google Drive.

    :param service: The Google Drive API service object.
    :param file_id: The ID of the file to retrieve versions for.
    :param fields: The fields to include in the response.
                   Default is "id, modifiedTime, originalFilename".
    :return: A list of file version dictionaries containing the specified
             fields.
    """
    try:
        # Get the list of revisions (versions) for the file
        revisions = (
            service.revisions()
            .list(
                fileId=file_id,
                fields=f"revisions({fields})",
            )
            .execute()
        )

        # Extract the revisions from the response
        return revisions.get("revisions", [])

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def gds_get_version_info(
    service,
    file_id,
    version_id,
    fields="id, originalFilename",
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
            service.revisions()
            .get(fileId=file_id, revisionId=version_id, fields=fields)
            .execute()
        )

        return revision

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def gds_get_file_info_shared_drive(
    service, file_id, fields="id, name, size, mimeType"
):
    """
    Retrieves specified fields of a file from a shared Google Drive.

    :param service: The Google Drive API service object.
    :param file_id: The ID of the file to retrieve information for.
    :param fields: The fields to include in the response.
                   Default is "id, name, size, mimeType".

    :return: A dictionary containing the specified fields of the file.
    """
    try:
        # Use the Google Drive API to get file information
        file_info = (
            service.files()
            .get(
                fileId=file_id,
                fields=fields,
                supportsAllDrives=True,
            )
            .execute()
        )

        return file_info

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_folders_hierarchy(service, drive_id):
    """
    Fetches the folder hierarchy of a shared Google Drive
    and organizes it into a nested dictionary structure.

    :param service: Authenticated Google Drive API service instance.
    :param drive_id: ID of the shared Google Drive.

    :return: A nested dictionary representing the folder hierarchy.
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

    :param drive_service: Authenticated Google Drive API service instance.
    :param drive_id: ID of the shared drive to upload the file to.
    :param file_path: Path to the file to upload.
    :param folder_id: ID of the folder to upload the file to (optional).
    :param description: Description of the file (optional).

    :return: The uploaded file metadata or None if an error occurs.
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
    try:

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

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


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

    :param service: Authenticated Google Drive API service instance.

    :return: List of the most recent files with their IDs and names.
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


def gds_revert_version(
    service, file_id, file_name, revision_id, revision_name
):
    """
    Reverts a file to a specific revision by downloading the revision content
    and uploading it as the current version.

    :param service: Authenticated Google Drive API service instance.
    :param file_id: ID of the file to revert.
    :param file_name: Name of the file to revert.
    :param revision_id: ID of the revision to revert to.
    :param revision_name: Name of the revision to revert to.
    and the file is in a shared drive).

    """
    # Step 1: Set the path to the Downloads folder
    download_folder = os.path.expanduser("~/Downloads")
    file_path = os.path.join(download_folder, revision_name)

    # Step 2: Download the specific revision
    try:
        request = service.revisions().get_media(
            fileId=file_id,
            revisionId=revision_id,
        )
        file_to_download = request.execute()

        with open(file_path, "wb") as temp_file:
            temp_file.write(file_to_download)
        print(f"File downloaded to {file_path}")

    except Exception as error:
        print(f"An error occurred while downloading the file: {error}")
        return

    # Step 3: Upload the downloaded file as the current version
    gds_upload_new_version(service, file_id, file_name, file_path)

    # Step 4: Delete the temporary downloaded file
    try:
        os.remove(file_path)
        print(f"File {file_path} deleted.")
    except Exception as error:
        print(f"An error occurred while deleting the file: {error}")


def gds_upload_new_version(service, file_id, file_name, file_path):
    """
    Uploads a new version of an existing file in Google Drive.

    :param service: Authenticated Google Drive API service instance.
    :param file_id: ID of the file to upload a new version for.
    :param file_name: Name of the file to upload.
    :param file_path: Path to the file to upload.

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

        # 1 change name on google drive
        name_version = os.path.basename(file_path)
        gds_rename_file(service, file_id, name_version)

        # 2 upload new version
        mime_type, _ = mimetypes.guess_type(name_version)
        if not mime_type:
            mime_type = "application/octet-stream"

        media = MediaFileUpload(file_path, resumable=True, mimetype=mime_type)

        updated_file = (
            service.files()
            .update(
                fileId=file_id,
                media_body=media,
                fields="id, name, size",
                supportsAllDrives=True,
            )
            .execute()
        )

        # 3 revert name on google drive
        gds_rename_file(service, file_id, file_name)

        print(
            f"New version {name_version} uploaded successfully for file ID: "
            f"{file_id}"
        )
        return updated_file

    except Exception as error:
        print(f"An error occurred: {error}")
        return None
