GCS Multi-Part Upload & Integrity Verification
=============================================

This project includes:
- A Python script to upload large files to Google Cloud Storage (GCS) in chunks
- A test suite using pytest to verify that the upload was successful and that the file is intact

Contents
--------
- upload_gcs.py     : Main uploader script (multi-threaded and chunked)
- test.py           : Tests for upload success and SHA-256 integrity
- README.txt        : This file

Uploader Script (upload_gcs.py)
-------------------------------
Features:
- Reads input from stdin in chunks and uploads to GCS
- Uses multiple threads for parallel uploading
- Automatically composes parts into a single GCS object
- Deletes intermediate parts after merging
- Designed for efficiency with large files

Usage:

    cat largefile.tar | python3 upload_gcs.py <destination_blob_name>
  or

    python3 upload_gcs.py <destination_blob_name> < largefile.tar

Testing (test.py)
-----------------
Test 1: Upload
- Creates a test file using random data
- Uploads the file to GCS
- Verifies the blob exists in the target bucket

Test 2: Integrity Check
- Downloads the uploaded blob
- Computes and compares SHA-256 hash to the original file

Final Cleanup:
- Deletes the uploaded GCS object
- Deletes the local test file

How to run tests:

    pytest test.py

Dependencies
------------
Install with pip:

    pip install google-cloud-storage google-crc32c pytest

Make sure your environment is authenticated with GCS:

    gcloud auth application-default login

Configuration
-------------
Set the bucket name at the top of the script:

    BUCKET_NAME = "analog-backups"

Notes
-----
- Composed objects in GCS do not include crc32c metadata
- SHA-256 is used to verify full file integrity
- Chunked uploads use 8 parallel threads by default
- Temporary files are named using UUIDs

Author
------
Andrii Omelianovych @ HaiLa Technologies
