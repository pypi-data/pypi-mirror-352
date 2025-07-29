#!/usr/bin/env python3
# Corey Goldberg, 2025
# License: MIT

"""Export your Google Drive data"""


import argparse
import io
import math
import os
import shutil
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


class GDriveExport:

    def __init__(self, working_dir, token_file, creds_file):
        self.working_dir = working_dir
        self.token_file = token_file
        self.creds_file = creds_file

        self.folder_cache = {}

        # If modifying these scopes, delete the `token.json` file
        self.scopes = [
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        self.creds = self._authenticate(self.scopes)
        self.service = build("drive", "v3", credentials=self.creds)
        self.files = self._get_files()
        self.files_map = self._map_files()

        for file_path, file_id in self.files_map.items():
            self._download_file(file_id, file_path)

    def _authenticate(self, scopes):
        # The token.json file stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, scopes)
        else:
            creds = None
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    # Token has probably expired or been revoked
                    creds = self._login(self.creds_file, scopes)
            else:
                creds = self._login(self.creds_file, scopes)
            # Save the credentials for the next run
            with open(self.token_file, "w") as f:
                f.write(creds.to_json())
        return creds

    def _login(self, creds_file, scopes):
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
        creds = flow.run_local_server(port=0)
        return creds

    def _download_file(self, file_id, file_path):
        request = self.service.files().get_media(fileId=file_id)
        bytes = io.BytesIO()
        try:
            downloader = MediaIoBaseDownload(bytes, request)
            while True:
                _, done = downloader.next_chunk()
                if done:
                    break
        except HttpError as e:
            # Only files with binary content can be downloaded, not native
            # Google App files (Docs/Sheets/Slides/Forms/etc)
            if (
                e.status_code == 403
                and e.error_details[0]["reason"] == "fileNotDownloadable"
                and "only files with binary content can be downloaded"
                in e.reason.lower()
            ):
                return None
            else:
                raise
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(file_path, "wb") as f:
            f.write(bytes.getvalue())
        print(f"Downloaded: {file_path}")
        return file_path

    def _get_files(self):
        about = self.service.about().get(fields="user").execute()
        email = about["user"]["emailAddress"]
        files = []
        page_token = None
        while True:
            results = (
                self.service.files()
                .list(
                    q=f"'{email}' in owners and mimeType!='application/vnd.google-apps.folder'",
                    spaces="drive",
                    fields="nextPageToken, files(id, name, parents)",
                    pageToken=page_token,
                )
                .execute()
            )
            files.extend(results.get("files", []))
            if not files:
                raise RuntimeError("No files found in Google Drive")
            page_token = results.get("nextPageToken", None)
            if page_token is None:
                break
        return files

    def _get_folder_path(self, folder_id):
        path_parts = []
        current_id = folder_id
        while current_id:
            if current_id in self.folder_cache:
                folder_name, parent_id = self.folder_cache[current_id]
            else:
                folder = (
                    self.service.files()
                    .get(fileId=current_id, fields="name, parents")
                    .execute()
                )
                folder_name = folder.get("name")
                parent_id = folder.get("parents", [None])[0]
                self.folder_cache[current_id] = (folder_name, parent_id)
            path_parts.insert(0, folder_name)  # Add to the front
            current_id = parent_id
        return os.path.sep.join(path_parts[1:])

    def _map_files(self):
        files_map = {}
        for f in self.files:
            folder_path = self._get_folder_path(f["parents"][0])
            file_path = os.path.join(self.working_dir, folder_path, f["name"])
            files_map[file_path] = f["id"]
        sorted_files_map = {key: files_map[key] for key in sorted(files_map)}
        return sorted_files_map


def dir_size(working_dir):
    """Size of a directory in bytes, including all subdirectories and files."""
    size_bytes = 0
    for entry in os.scandir(working_dir):
        if entry.is_file():
            size_bytes += entry.stat().st_size
        elif entry.is_dir():
            size_bytes += dir_size(entry.path)
    return size_bytes


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    sizes = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {sizes[i]}"


def run(working_dir):
    cur_dir = os.getcwd()
    token_file = os.path.join(".", "token.json")
    creds_file = os.path.join(".", "credentials.json")
    if not os.path.exists(creds_file):
        sys.exit(f"Can't find required file: {creds_file}")
    if os.path.exists(working_dir):
        overwrite = input(
            f"The '{os.path.basename(working_dir)}' directory already exists. Overwrite? [y/N] "
        ).lower()
        if overwrite in ("y", "yes"):
            shutil.rmtree(working_dir)
        else:
            sys.exit("Exiting so files are not overwritten")
    print(f"\nExporting files to: {working_dir}\n")
    try:
        GDriveExport(working_dir, token_file, creds_file)
    except (HttpError, RuntimeError) as e:
        sys.exit(f"Error: {e}")
    size = convert_size(dir_size(working_dir))
    print(f"\nTotal size: {size}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".", help="output directory")
    args = parser.parse_args()
    try:
        working_dir = os.path.join(args.dir, "exported_files")
        run(working_dir)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
