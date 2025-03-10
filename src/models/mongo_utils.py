from pymongo.mongo_client import MongoClient

uri = (
    "mongodb+srv://famkedewachterplugin:wpsvSnfyistiZeRs@"
    "cluster0.kweyp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Create a new client and connect to the server
client = MongoClient(uri)

# Select the database and collection
db = client["google_drive"]
revisions_collection = db["revisions"]


def mongo_save_description(file_id, version_id, description):
    """
    Saves or updates the description of a file revision in MongoDB.
    If a revision with the same file_id already exists, it will add the new
    version_id and description.
    Otherwise, a new revision will be created.

    Args:
        file_id (str): The ID of the file.
        version_id (str): The ID of the version.
        description (str): The description of the version.
    """
    query = {"file_id": file_id}

    # Define the update operation to push the
    # new version and description into an array
    update = {
        "$push": {
            "versions": {"version_id": version_id, "description": description}
        }
    }

    # Use upsert=True to update if exists, or insert if not
    revisions_collection.update_one(query, update, upsert=True)


def mongo_get_version_description(file_id, version_id):
    """
    Retrieves the description of a specific version of a file.

    Args:
        file_id (str): The ID of the file.
        version_id (str): The ID of the version.

    Returns:
        str: The description of the version,
        or None if the version or file is not found.
    """
    query = {"file_id": file_id, "versions.version_id": version_id}
    projection = {"versions.$": 1}  # Only return the matching version

    result = revisions_collection.find_one(query, projection)

    if result and "versions" in result:
        return result["versions"][0]["description"]

    return None
