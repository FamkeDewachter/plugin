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
            .update(
                fileId=file_id,
                body=file_metadata,
                fields="id, name",
                supportsAllDrives=True,
            )
            .execute()
        )
        return updated_file

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
