# MapHub

[![PyPI Version](https://img.shields.io/pypi/v/maphub.svg)](https://pypi.org/project/maphub/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/maphub.svg?label=PyPI%20downloads)](
https://pypi.org/project/maphub/)


## Installation
### pip
```sh 
pip install maphub
```

## Usage

### Python package
This example demonstrates how to upload a Map from the local path to a MapHub folder with the name `France`.
```python 
from maphub import MapHubClient

client = MapHubClient(api_key="your-api-key")
personal_workspace = client.workspace.get_personal_workspace()
root_folder = client.folder.get_root_folder(personal_workspace["id"])
france_folder = client.folder.create_folder("France", root_folder["folder"]["id"])

client.maps.upload_map(
    map_name="France Population",
    folder_id=france_folder['id'],
    public=False,
    path="path/to/GIS/data.gpkg"
)
```

> **Note**: The direct endpoint methods (e.g., `client.create_project()`, `client.upload_map()`) are deprecated and will be removed in a future version. Use the endpoint classes instead (e.g., `client.folder.create_folder()`, `client.map.upload_map()`).

### CLI
The MapHub CLI provides a command-line interface for interacting with the MapHub API. It allows you to authenticate with an API key and upload maps to your folders.

#### Authentication
Before using the CLI, you need to authenticate with your MapHub API key:

```sh
maphub auth YOUR_API_KEY
```

This will save your API key to `~/.maphub/config.json` for future use.

#### Uploading Maps
To upload a GIS file to your root folder:

```sh
maphub upload path/to/your/file.gpkg
```

The map name will be extracted from the file name (without extension).

To upload a GIS file to a specific folder:

```sh
maphub upload path/to/your/file.gpkg --folder-id YOUR_FOLDER_ID
```

If you don't specify a folder ID, the map will be uploaded to your root folder.

To upload a GIS file with a custom map name:

```sh
maphub upload path/to/your/file.gpkg --map-name "My Custom Map Name"
```

If you don't specify a map name, it will be extracted from the file name (without extension).

#### Cloning Maps and Folders
To clone a map or folder from MapHub to your local machine:

```sh
maphub clone MAP_OR_FOLDER_ID
```

This will clone the map or folder to the current directory.

To specify an output directory:

```sh
maphub clone MAP_OR_FOLDER_ID --output path/to/output/directory
```

#### Pulling Changes
To pull the latest changes from MapHub to your local clone:

```sh
maphub pull
```

This command should be run from within a directory that was previously cloned. It will update any maps that have changed on the server.

#### Pushing Changes
To push your local changes back to MapHub:

```sh
maphub push
```

This command should be run from within a directory that was previously cloned. It will upload any maps that have changed locally.
