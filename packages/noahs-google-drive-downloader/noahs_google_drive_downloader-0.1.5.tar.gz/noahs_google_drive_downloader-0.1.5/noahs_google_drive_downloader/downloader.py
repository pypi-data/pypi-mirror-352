

import os
import sys
import subprocess
import gdown
import re
import zipfile


def extract_file_id(url):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    raise ValueError("Could not extract file ID from URL.")


def clean_google_drive_url(url):
    if "folders/" in url:
        return url.split("?")[0]
    return url


def extract_zip_if_needed(file_path, delete_zip=True, quiet=False):
    if file_path.endswith(".zip") and os.path.isfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()

            # Detect if all files are inside a single top-level folder
            top_dirs = {p.split("/")[0] for p in zip_contents if "/" in p}
            single_root = len(top_dirs) == 1

            extract_dir = os.path.dirname(file_path) if single_root else os.path.splitext(file_path)[0]

            if not quiet:
                print(f"[INFO] Extracting ZIP file: {file_path} to {extract_dir}")
            zip_ref.extractall(extract_dir)

        if delete_zip:
            os.remove(file_path)
            if not quiet:
                print(f"[CLEANUP] Deleted ZIP file: {file_path}")
        return extract_dir
    return None



def download_google_drive_folder(folder_url, output_dir, redundancy_check=True, quiet=False, use_cookies=False, extract_zip_files=False):
    folder_url = clean_google_drive_url(folder_url)
    if redundancy_check:
        if os.path.exists(output_dir) and os.listdir(output_dir):
            if not quiet:
                print(f"[INFO] Skipping download. Directory '{output_dir}' already exists and contains files.")
            return
    os.makedirs(output_dir, exist_ok=True)
    if not quiet:
        print(f"[INFO] Downloading folder from: {folder_url}")
    gdown.download_folder(url=folder_url, output=output_dir, quiet=quiet, use_cookies=use_cookies)

    if extract_zip_files:
        # Check for zip files in the folder and extract them
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".zip"):
                    zip_path = os.path.join(root, file)
                    extract_zip_if_needed(zip_path, quiet=quiet)

    if not quiet:
        print(f"[SUCCESS] Folder and ZIP extraction complete: {output_dir}")


def download_google_drive_file(url, output_path, redundancy_check=True, quiet=False, use_cookies=False, extract_zip_files=True):
    if redundancy_check and os.path.exists(output_path):
        if not quiet:
            print(f"[SKIPPED] File already exists: {output_path}")
        return output_path
    
    try:
        file_id = extract_file_id(url)
        direct_url = f"https://drive.google.com/uc?id={file_id}"
    except ValueError as e:
        print(f"[ERROR] {e}")
        return None

    downloaded_file = gdown.download(direct_url, output=output_path, quiet=quiet, use_cookies=use_cookies)
    if downloaded_file:
        if not quiet:
            print(f"[SUCCESS] File downloaded to: {downloaded_file}")
        if extract_zip_files:
            extract_zip_if_needed(downloaded_file, quiet=quiet)
        return downloaded_file
    else:
        if not quiet:
            print("[ERROR] Download failed.")
        return None












































