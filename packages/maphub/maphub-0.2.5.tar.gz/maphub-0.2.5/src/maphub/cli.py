#!/usr/bin/env python3
"""
MapHub CLI - Command-line interface for MapHub API.

This module provides a command-line interface for interacting with the MapHub API.
It allows users to authenticate with an API key and upload maps to their projects.
"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .client import MapHubClient
from .exceptions import APIException

# Define the config directory and file path
CONFIG_DIR = Path.home() / ".maphub"
CONFIG_FILE = CONFIG_DIR / "config.json"


def __get_api_client__() -> MapHubClient:
    """
    Initializes and returns an instance of MapHubClient using the provided API key
    stored in the configuration file. If the configuration file does not exist or
    the JSON is invalid, the program will print an error message and terminate.

    :return: An instance of MapHubClient initialized with the API key if found in
             the configuration file.
    :rtype: MapHubClient
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            api_key = config.get("api_key")
            return MapHubClient(api_key=api_key)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Error: No API key found. Please run 'maphub auth API_KEY' first.", file=sys.stderr)
        sys.exit(1)


def save_api_key(api_key: str) -> None:
    """
    Save the API key to the local configuration file.

    Args:
        api_key: The API key to save
    """
    # Create the config directory if it doesn't exist
    CONFIG_DIR.mkdir(exist_ok=True)

    # Save the API key to the config file
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)

    print(f"API key saved successfully to {CONFIG_FILE}")



def auth_command(args) -> None:
    """
    Handle the 'auth' command to save the API key.

    Args:
        args: Command-line arguments
    """
    save_api_key(args.api_key)


def upload_command(args) -> None:
    """
    Handle the 'upload' command to upload a GIS file.

    Args:
        args: Command-line arguments
    """
    # Check if the file exists
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Create the client
    client = __get_api_client__()

    try:
        # Use the provided folder_id if available, otherwise use the root folder
        folder_id = args.folder_id
        if folder_id is None:
            # If error occurs when getting folders, fall back to root folder
            personal_workspace = client.workspace.get_personal_workspace()
            root_folder = client.folder.get_root_folder(personal_workspace["id"])
            folder_id = root_folder["folder"]["id"]
            print(f"Using root folder (ID: {folder_id})")
        else:
            print(f"Using specified folder (ID: {folder_id})")

        # Use the provided map_name if available, otherwise extract from the file path (without extension)
        map_name = args.map_name if args.map_name else file_path.stem

        # Upload the map
        print(f"Uploading {file_path} to folder {folder_id}...")
        response = client.maps.upload_map(
            map_name=map_name,
            folder_id=folder_id,
            public=False,
            path=str(file_path)
        )

        print(f"Map uploaded successfully!")

    except APIException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


# Helper functions for clone, pull, and push commands

def calculate_checksum(file_path: str) -> str:
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_path_for_map(map_data: Dict[str, Any], save_dir: Path) -> str:
    """
    Determine the file path for a map based on its type.

    Args:
        map_data: Map metadata
        save_dir: Directory to save the map in

    Returns:
        File path for the map
    """
    fall_back_name = f"map_{map_data.get('id')}"
    file_name = f"{map_data.get('name', fall_back_name)}"

    if map_data.get('type') == 'raster':
        file_name += ".tif"
    elif map_data.get('type') == 'vector':
        file_name += ".fgb"
    else:
        # Default to .gpkg if type is not specified
        file_name += ".gpkg"

    return os.path.join(save_dir, file_name)


def find_repository_root() -> Optional[Path]:
    """
    Find the root directory of the MapHub repository (containing .maphub).

    Returns:
        Path to the repository root, or None if not in a repository
    """
    current_dir = Path.cwd()
    root_dir = current_dir

    while not (root_dir / ".maphub").exists():
        if root_dir.parent == root_dir:  # Reached filesystem root
            return None
        root_dir = root_dir.parent

    return root_dir


def save_map_metadata(map_data: Dict[str, Any], map_id: uuid.UUID, file_path: str, 
                      output_dir: Path, maphub_dir: Path) -> Dict[str, Any]:
    """
    Save metadata for a map.

    Args:
        map_data: Map metadata from the API
        map_id: UUID of the map
        file_path: Path to the map file
        output_dir: Root directory of the repository
        maphub_dir: Path to the .maphub directory

    Returns:
        Map metadata dictionary
    """
    # Save map metadata - use the checksum from the metadata if available
    map_metadata = {
        "id": str(map_id),
        "version_id": map_data.get("latest_version_id", None),
        "checksum": map_data.get("checksum", calculate_checksum(file_path)),
        "path": str(Path(file_path).relative_to(output_dir)),
        "last_modified": map_data.get("updated_at"),
        "type": map_data.get("type", "unknown")
    }

    with open(maphub_dir / "maps" / f"{map_id}.json", "w") as f:
        json.dump(map_metadata, f, indent=2)

    return map_metadata


def save_folder_metadata(folder_id: uuid.UUID, folder_name: str, parent_id: Optional[str], 
                         maps: List[str], subfolders: List[str], maphub_dir: Path) -> None:
    """
    Save metadata for a folder.

    Args:
        folder_id: UUID of the folder
        folder_name: Name of the folder
        parent_id: UUID of the parent folder, or None if root
        maps: List of map IDs in the folder
        subfolders: List of subfolder IDs in the folder
        maphub_dir: Path to the .maphub directory
    """
    folder_metadata = {
        "id": str(folder_id),
        "name": folder_name,
        "parent_id": parent_id,
        "maps": maps,
        "subfolders": subfolders
    }

    with open(maphub_dir / "folders" / f"{folder_id}.json", "w") as f:
        json.dump(folder_metadata, f, indent=2)


def save_folder_metadata_recursive(client: MapHubClient, folder_id: uuid.UUID, 
                                  root_dir: Path, maphub_dir: Path) -> None:
    """
    Recursively save metadata for a folder and its subfolders.

    This function assumes that the folder structure has already been created
    and the maps have already been downloaded.

    Args:
        client: MapHub API client
        folder_id: UUID of the folder
        root_dir: Root directory of the repository
        maphub_dir: Path to the .maphub directory
    """
    folder_info = client.folder.get_folder(folder_id)
    folder_name = folder_info.get("folder", {}).get("name", "root")

    # Get maps and subfolders
    map_ids = []
    subfolder_ids = []

    # Process maps - just collect IDs, don't try to save metadata for maps that might not exist
    maps = folder_info["map_infos"]
    for map_data in maps:
        map_id = uuid.UUID(map_data["id"])
        map_ids.append(str(map_id))

    # Process subfolders
    subfolders = folder_info["child_folders"]

    for subfolder in subfolders:
        subfolder_id = uuid.UUID(subfolder["id"])
        subfolder_ids.append(str(subfolder_id))

        # Recursively save metadata for subfolders
        save_folder_metadata_recursive(client, subfolder_id, root_dir / folder_name, maphub_dir)

    # Save folder metadata
    parent_id = folder_info.get("folder", {}).get("parent_folder_id")
    save_folder_metadata(folder_id, folder_name, parent_id, map_ids, subfolder_ids, maphub_dir)


# Map operation functions

def clone_map(client: MapHubClient, map_id: uuid.UUID, output_dir: Path, maphub_dir: Path) -> None:
    """
    Clone a single map from MapHub.

    Args:
        client: MapHub API client
        map_id: UUID of the map to clone
        output_dir: Directory to save the map in
        maphub_dir: Path to the .maphub directory
    """
    try:
        map_data = client.maps.get_map(map_id)
        print(f"Cloning map: {map_data.get('name', 'Unnamed Map')}")

        # Get the file path for the map
        file_path = get_file_path_for_map(map_data, output_dir)

        # Download the map
        client.maps.download_map(map_id, file_path)

        # Save map metadata
        save_map_metadata(map_data, map_id, file_path, output_dir, maphub_dir)

        print(f"Successfully cloned map to {file_path}")
    except Exception as e:
        print(f"Error cloning map {map_id}: {e}")
        raise


def pull_map(client: MapHubClient, map_id: uuid.UUID, map_metadata: Dict[str, Any], 
            root_dir: Path, maphub_dir: Path) -> None:
    """
    Pull updates for a single map from MapHub.

    Args:
        client: MapHub API client
        map_id: UUID of the map to pull
        map_metadata: Current map metadata
        root_dir: Root directory of the repository
        maphub_dir: Path to the .maphub directory
    """
    try:
        # Get the latest map info
        map_data = client.maps.get_map(map_id)

        # Check if the version has changed
        if map_data.get('map').get("latest_version_id") != map_metadata["version_id"]:
            print(f"Pulling updates for map: {map_data.get('map', {}).get('name', 'Unnamed Map')}")

            # Get the current map path
            map_path = root_dir / map_metadata["path"]

            # Get the new file path for the map
            file_path = get_file_path_for_map(map_data.get('map'), map_path.parent)

            # Download the map
            client.maps.download_map(map_id, file_path)

            # Update metadata
            map_metadata["version_id"] = map_data.get("version_id", str(uuid.uuid4()))
            map_metadata["checksum"] = map_data.get("checksum", calculate_checksum(file_path))
            map_metadata["last_modified"] = map_data.get("updated_at")
            map_metadata["path"] = str(Path(file_path).relative_to(root_dir))
            map_metadata["type"] = map_data.get("type", "unknown")

            with open(maphub_dir / "maps" / f"{map_id}.json", "w") as f:
                json.dump(map_metadata, f, indent=2)

            print(f"Successfully updated map: {map_data.get('map', {}).get('name', 'Unnamed Map')}")
        else:
            print(f"Map is already up to date: {map_data.get('map', {}).get('name', 'Unnamed Map')}")
    except Exception as e:
        print(f"Error pulling map {map_id}: {e}")


def push_map(client: MapHubClient, map_id: uuid.UUID, map_metadata: Dict[str, Any], 
            folder_id: uuid.UUID, root_dir: Path, maphub_dir: Path) -> None:
    """
    Push updates for a single map to MapHub.

    Args:
        client: MapHub API client
        map_id: UUID of the map to push
        map_metadata: Current map metadata
        folder_id: UUID of the folder containing the map
        root_dir: Root directory of the repository
        maphub_dir: Path to the .maphub directory
    """
    try:
        # Check if the local file has changed
        map_path = root_dir / map_metadata["path"]

        if not map_path.exists():
            print(f"Warning: Map file not found: {map_path}")
            return

        current_checksum = calculate_checksum(str(map_path))

        if current_checksum != map_metadata["checksum"]:
            print(f"Pushing updates for map: {map_path.stem}")

            # Upload the updated map
            response = client.maps.upload_map(
                map_name=map_path.stem,
                folder_id=folder_id,
                public=False,
                path=str(map_path)
            )

            # Update metadata
            map_metadata["version_id"] = response.get("version_id", str(uuid.uuid4()))
            map_metadata["checksum"] = response.get("checksum", current_checksum)
            map_metadata["last_modified"] = response.get("updated_at")

            with open(maphub_dir / "maps" / f"{map_id}.json", "w") as f:
                json.dump(map_metadata, f, indent=2)

            print(f"Successfully pushed map updates: {map_path.stem}")
        else:
            print(f"No changes to push for map: {map_path.stem}")
    except Exception as e:
        print(f"Error pushing map {map_id}: {e}")


# Folder operation functions

def clone_folder(client: MapHubClient, folder_id: uuid.UUID, local_path: Path, 
                output_dir: Path, maphub_dir: Optional[Path]) -> Path:
    """
    Recursively clone a folder and its contents from MapHub.

    Args:
        client: MapHub API client
        folder_id: UUID of the folder to clone
        local_path: Local path to save the folder in
        output_dir: Root directory of the repository
        maphub_dir: Path to the .maphub directory, or None if metadata should not be saved yet

    Returns:
        Path to the cloned folder
    """
    try:
        folder_info = client.folder.get_folder(folder_id)
        folder_name = folder_info.get("folder", {}).get("name", "root")

        print(f"Cloning folder: {folder_name}")

        # Create local folder
        folder_path = local_path / folder_name
        folder_path.mkdir(exist_ok=True)

        # Track maps and subfolders
        map_ids = []
        subfolder_ids = []

        # Clone maps in this folder
        maps = folder_info["map_infos"]
        for map_data in maps:
            map_id = uuid.UUID(map_data["id"])

            print(f"  Cloning map: {map_data.get('name', 'Unnamed Map')}")

            # Get the file path for the map
            file_path = get_file_path_for_map(map_data, folder_path)

            # Download the map
            client.maps.download_map(map_id, file_path)

            # Save map metadata if maphub_dir is provided
            if maphub_dir is not None:
                save_map_metadata(map_data, map_id, file_path, output_dir, maphub_dir)

            map_ids.append(str(map_id))


        # Recursively clone subfolders
        subfolders = folder_info["child_folders"]

        for subfolder in subfolders:
            subfolder_id = uuid.UUID(subfolder["id"])
            subfolder_ids.append(str(subfolder_id))
            clone_folder(client, subfolder_id, folder_path, output_dir, maphub_dir)

        # Save folder metadata if maphub_dir is provided
        if maphub_dir is not None:
            parent_id = folder_info.get("folder", {}).get("parent_folder_id")
            save_folder_metadata(folder_id, folder_name, parent_id, map_ids, subfolder_ids, maphub_dir)

        return folder_path
    except Exception as e:
        print(f"Error cloning folder {folder_id}: {e}")
        import traceback
        traceback.print_exc()
        return local_path


def pull_folder(client: MapHubClient, folder_id: uuid.UUID, local_path: Path, 
               root_dir: Path, maphub_dir: Path) -> None:
    """
    Recursively pull updates for a folder and its contents from MapHub.

    Args:
        client: MapHub API client
        folder_id: UUID of the folder to pull
        local_path: Local path of the folder
        root_dir: Root directory of the repository
        maphub_dir: Path to the .maphub directory
    """
    folder_file = maphub_dir / "folders" / f"{folder_id}.json"

    if not folder_file.exists():
        print(f"Warning: Folder metadata not found for {folder_id}")
        return

    with open(folder_file, "r") as f:
        folder_metadata = json.load(f)

    folder_info = client.folder.get_folder(folder_id)
    folder_name = folder_info.get("folder", {}).get("name", "root")

    print(f"Checking folder: {folder_name}")

    # Pull maps in this folder
    for map_id in folder_metadata["maps"]:
        map_file = maphub_dir / "maps" / f"{map_id}.json"

        if not map_file.exists():
            print(f"Warning: Map metadata not found for {map_id}")
            continue

        with open(map_file, "r") as f:
            map_metadata = json.load(f)

        pull_map(client, uuid.UUID(map_id), map_metadata, root_dir, maphub_dir)

    # Recursively pull subfolders
    for subfolder_id in folder_metadata["subfolders"]:
        subfolder_file = maphub_dir / "folders" / f"{subfolder_id}.json"

        if not subfolder_file.exists():
            print(f"Warning: Subfolder metadata not found for {subfolder_id}")
            continue

        with open(subfolder_file, "r") as f:
            subfolder_metadata = json.load(f)

        subfolder_path = local_path / subfolder_metadata["name"]
        pull_folder(client, uuid.UUID(subfolder_id), subfolder_path, root_dir, maphub_dir)


def push_folder(client: MapHubClient, folder_id: uuid.UUID, local_path: Path, 
               root_dir: Path, maphub_dir: Path) -> None:
    """
    Recursively push updates for a folder and its contents to MapHub.

    Args:
        client: MapHub API client
        folder_id: UUID of the folder to push
        local_path: Local path of the folder
        root_dir: Root directory of the repository
        maphub_dir: Path to the .maphub directory
    """
    folder_file = maphub_dir / "folders" / f"{folder_id}.json"

    if not folder_file.exists():
        print(f"Warning: Folder metadata not found for {folder_id}")
        return

    with open(folder_file, "r") as f:
        folder_metadata = json.load(f)

    folder_info = client.folder.get_folder(folder_id)
    folder_name = folder_info.get("folder", {}).get("name", "root")

    print(f"Checking folder: {folder_name}")

    # Push maps in this folder
    for map_id in folder_metadata["maps"]:
        map_file = maphub_dir / "maps" / f"{map_id}.json"

        if not map_file.exists():
            print(f"Warning: Map metadata not found for {map_id}")
            continue

        with open(map_file, "r") as f:
            map_metadata = json.load(f)

        push_map(client, uuid.UUID(map_id), map_metadata, folder_id, root_dir, maphub_dir)

    # Recursively push subfolders
    for subfolder_id in folder_metadata["subfolders"]:
        subfolder_file = maphub_dir / "folders" / f"{subfolder_id}.json"

        if not subfolder_file.exists():
            print(f"Warning: Subfolder metadata not found for {subfolder_id}")
            continue

        with open(subfolder_file, "r") as f:
            subfolder_metadata = json.load(f)

        subfolder_path = local_path / subfolder_metadata["name"]
        push_folder(client, uuid.UUID(subfolder_id), subfolder_path, root_dir, maphub_dir)


# Main command functions

def clone_command(args) -> None:
    """
    Clone a map or folder from MapHub to local directory.

    Args:
        args: Command-line arguments containing:
            - id: ID of the map or folder to clone
            - output: Path to the output directory
    """
    # Create the client
    client = __get_api_client__()

    # Get the ID from args
    resource_id = uuid.UUID(args.id)
    output_dir = Path(args.output).resolve()

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Try to get as map first
    try:
        # For maps, create .maphub directory in the output directory
        maphub_dir = output_dir / ".maphub"
        maphub_dir.mkdir(exist_ok=True)
        (maphub_dir / "maps").mkdir(exist_ok=True)
        (maphub_dir / "folders").mkdir(exist_ok=True)

        # Save config
        with open(maphub_dir / "config.json", "w") as f:
            json.dump({
                "remote_id": str(resource_id),
                "last_sync": datetime.now().isoformat()
            }, f, indent=2)

        clone_map(client, resource_id, output_dir, maphub_dir)
        return
    except Exception as e:
        # Not a map, try as folder
        print(f"Not a map or error occurred: {e}. Trying as folder...")

    # Try to get as folder
    try:
        # For folders, first clone the folder structure
        result_path = clone_folder(client, resource_id, output_dir, output_dir, None)

        # Then create .maphub directory inside the cloned folder
        maphub_dir = result_path / ".maphub"
        maphub_dir.mkdir(exist_ok=True)
        (maphub_dir / "maps").mkdir(exist_ok=True)
        (maphub_dir / "folders").mkdir(exist_ok=True)

        # Save config
        with open(maphub_dir / "config.json", "w") as f:
            json.dump({
                "remote_id": str(resource_id),
                "last_sync": datetime.now().isoformat()
            }, f, indent=2)

        # Now save metadata for the folder and its contents
        folder_info = client.folder.get_folder(resource_id)
        folder_name = folder_info.get("folder", {}).get("name", "root")

        # Get maps and subfolders
        map_ids = []
        subfolder_ids = []

        # Process maps
        maps = folder_info["map_infos"]
        for map_data in maps:
            map_id = uuid.UUID(map_data["id"])
            map_ids.append(str(map_id))

            # Save map metadata
            file_path = get_file_path_for_map(map_data, result_path)
            save_map_metadata(map_data, map_id, file_path, result_path, maphub_dir)

        # Process subfolders
        subfolders = folder_info["child_folders"]

        for subfolder in subfolders:
            subfolder_id = uuid.UUID(subfolder["id"])
            subfolder_ids.append(str(subfolder_id))

            # Save subfolder metadata recursively
            save_folder_metadata_recursive(client, subfolder_id, result_path, maphub_dir)

        # Save folder metadata
        parent_id = folder_info.get("folder", {}).get("parent_folder_id")
        save_folder_metadata(resource_id, folder_name, parent_id, map_ids, subfolder_ids, maphub_dir)

        print(f"Successfully cloned folder structure to {result_path}")
    except Exception as e:
        print(f"Error: Failed to clone resource with ID {resource_id}: {e}")
        import traceback
        traceback.print_exc()
        return


def pull_command(args) -> None:
    """
    Pull latest changes from MapHub.

    This command should be run from within a directory that was previously cloned.
    It will update any maps that have changed on the server.
    """
    # Find the root directory (containing .maphub)
    root_dir = find_repository_root()
    if root_dir is None:
        print("Error: Not in a MapHub repository. Please run this command from within a cloned directory.", file=sys.stderr)
        sys.exit(1)

    maphub_dir = root_dir / ".maphub"

    # Load config
    try:
        with open(maphub_dir / "config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load MapHub configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Create the client
    client = __get_api_client__()

    # Get the remote ID
    remote_id = uuid.UUID(config["remote_id"])

    # Try to pull as map
    try:
        # Check if it's a map
        map_file = maphub_dir / "maps" / f"{remote_id}.json"
        if map_file.exists():
            with open(map_file, "r") as f:
                map_metadata = json.load(f)

            pull_map(client, remote_id, map_metadata, root_dir, maphub_dir)

            # Update config
            config["last_sync"] = datetime.now().isoformat()
            with open(maphub_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)

            return
    except Exception as e:
        # Not a map, try as folder
        print(f"Not a map or error occurred: {e}. Trying as folder...")

    # Start pulling from the root folder
    try:
        pull_folder(client, remote_id, root_dir, root_dir, maphub_dir)

        # Update config
        config["last_sync"] = datetime.now().isoformat()
        with open(maphub_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        print("Pull completed successfully")
    except Exception as e:
        print(f"Error during pull: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def push_command(args) -> None:
    """
    Push local changes to MapHub.

    This command should be run from within a directory that was previously cloned.
    It will upload any maps that have changed locally.
    """
    # Find the root directory (containing .maphub)
    root_dir = find_repository_root()
    if root_dir is None:
        print("Error: Not in a MapHub repository. Please run this command from within a cloned directory.", file=sys.stderr)
        sys.exit(1)

    maphub_dir = root_dir / ".maphub"

    # Load config
    try:
        with open(maphub_dir / "config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load MapHub configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Create the client
    client = __get_api_client__()

    # Get the remote ID
    remote_id = uuid.UUID(config["remote_id"])

    # Try to push as map
    try:
        # Check if it's a map
        map_file = maphub_dir / "maps" / f"{remote_id}.json"
        if map_file.exists():
            with open(map_file, "r") as f:
                map_metadata = json.load(f)

            # Get map info to get the folder_id
            map_info = client.maps.get_map(remote_id)
            folder_id = map_info.get("folder_id")

            if not folder_id:
                # If no folder_id, get the root folder
                personal_workspace = client.workspace.get_personal_workspace()
                root_folder = client.folder.get_root_folder(personal_workspace["id"])
                folder_id = root_folder["folder"]["id"]

            push_map(client, remote_id, map_metadata, uuid.UUID(folder_id), root_dir, maphub_dir)

            # Update config
            config["last_sync"] = datetime.now().isoformat()
            with open(maphub_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)

            return
    except Exception as e:
        # Not a map, try as folder
        print(f"Not a map or error occurred: {e}. Trying as folder...")

    # Start pushing from the root folder
    try:
        push_folder(client, remote_id, root_dir, root_dir, maphub_dir)

        # Update config
        config["last_sync"] = datetime.now().isoformat()
        with open(maphub_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        print("Push completed successfully")
    except Exception as e:
        print(f"Error during push: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(description="MapHub CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Save API key")
    auth_parser.add_argument("api_key", help="MapHub API key (Can be created here: https://www.maphub.co/dashboard/api_keys)")
    auth_parser.set_defaults(func=auth_command)

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a GIS file")
    upload_parser.add_argument("file_path", help="Path to the GIS file")
    upload_parser.add_argument("--folder-id", help="Target folder ID (uses root folder if not specified)", default=None)
    upload_parser.add_argument("--map-name", help="Custom map name (uses file name if not specified)", default=None)
    upload_parser.set_defaults(func=upload_command)

    # Clone command
    clone_parser = subparsers.add_parser("clone", help="Clone a Map or Folder")
    clone_parser.add_argument("id", help="ID of the Map or Folder to clone")
    clone_parser.add_argument("--output", help="The path to the desired output folder.", default=".")
    clone_parser.set_defaults(func=clone_command)

    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull latest version from a Map or Folder on MapHub")
    pull_parser.set_defaults(func=pull_command)

    # Push command
    push_parser = subparsers.add_parser("push", help="Push local version of a Map or Folder to MapHub")
    push_parser.set_defaults(func=push_command)


    # Parse arguments
    args = parser.parse_args()

    # Execute the appropriate command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
