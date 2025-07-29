# google-drive-export

### Export your Google Drive data

- Copyright (c) 2025 [Corey Goldberg][github-home]
- License: [MIT][mit-license]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi]

[github-home]: https://github.com/cgoldberg
[mit-license]: https://raw.githubusercontent.com/cgoldberg/google-drive-export/refs/heads/master/LICENSE
[github-repo]: https://github.com/cgoldberg/google-drive-export
[pypi]: https://pypi.org/project/google-drive-export

----

## About:

This is a command line tool for exporting your personal Google Drive files using the Google Drive API v3.

It will export all files that are owned by your account (not shared with you from other users), and
will not save native Google App files (Docs/Sheets/Slides/Forms/etc). Files are saved in their appropriate
directory structure inside a directory named `exported_files`.

For more information:
- [API Overview][api-overview]
- [REST API Reference][api-reference]
- [API Guides][api-guides]

[api-overview]: https://developers.google.com/workspace/drive/api
[api-reference]: https://developers.google.com/workspace/drive/api/reference/rest/v3
[api-guides]: https://developers.google.com/workspace/drive/api/guides/about-files

----

## Requirements:

- Python 3.9+
- Packages:
  - google-api-python-client
  - google-auth-httplib2
  - google-auth-oauthlib

----

## Usage:

```
usage: google_drive_export [-h] [--dir DIR]

options:
  -h, --help  show this help message and exit
  --dir DIR   output directory
```

----

## Installation:

### Create a virtual environment and install with pip

- On Linux/Mac:

```
python3 -m venv venv
source venv/bin/activate
pip install google-drive-export
```

- On Windows:

```
py -m venv venv
venv\Scripts\activate
pip install google-drive-export
```

For more information on virtual env and pip, see:
- https://packaging.python.org/en/latest/tutorials/installing-packages

### Install globally with pipx

```
pipx install google-drive-export
```

For more information on pipx, see:
- https://github.com/pypa/pipx

----

## Authorization for use with Google Drive:

After installing, you must follow these steps:

### 1. Enable the Google Drive API

- Go to the Google Cloud console (Enable access to API)
  - https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com
- Create a Project
- Enable the API

### 2. Configure the OAuth Consent screen

- Go to the Google Cloud console (Branding)
  - https://console.cloud.google.com/auth/branding
- Configure your Project
- Go to the Google Cloud console (Audience)
  - https://console.cloud.google.com/auth/audience
- Add yourself as a Test user

### 3. Authorize credentials for a desktop application

- Go to the Google Cloud console (Clients)
  - https://console.cloud.google.com/auth/clients
  - Create a Client (Application type > Desktop app)
  - Downloaded JSON file, rename it to credentials.json, and move it to your working directory

### 4. Run the program

```
google_drive_export
```

- The first time you run it, a browser window will open and you will be prompted to authorize access to your Google account:
  - If you are not already signed in to your Google Account, sign in when prompted
  - If you are signed in to multiple accounts, select the account to use for authorization
  - Click Accept
- Authorization information is stored in the file system (`token.json`), so the next time you run it, you aren't prompted for authorization
