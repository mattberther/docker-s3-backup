#!/usr/bin/python

import datetime
import os
import string
import tarfile

import boto3
from botocore.exceptions import ClientError

from glob import glob
from datetime import timedelta

# Configuration
aws_bucket = os.environ['AWS_S3_BUCKET']

dirs = glob('/data/*/')

# Script Configuration
today = datetime.date.today()
previous = today - timedelta(days=7)

# Establish S3 Connection
s3_client = boto3.client('s3')

# File Backups
for d in dirs:
    print(f'[FILE] Found directory {d}')
    file = d.rstrip(os.sep).split(os.sep)[::-1][0]
    filename = f'{file}-{str(today)}.files.tar.gz'
    out_file = os.path.join('/tmp', filename)

    print(f'[FILE] Creating archive for {file}')

    tar = tarfile.open(out_file, 'w:gz')
    tar.add(d)
    tar.close()

    print(f'[S3] Uploading file archive {file}...')
    try:
        resp = s3_client.upload_file(out_file, aws_bucket, filename)
    except ClientError as e:
        logging.error(e)
        continue

    os.remove(out_file)

    print(f'[S3] Clearing previous file archive {file}...')

    # Preserve monthly backups (Previous Month)
    if previous != str(datetime.datetime.today().year) + '-' + str(datetime.datetime.today().month) + '-1':
        # Clean up files on S3
        s3_client.delete_object(Bucket=aws_bucket, Key=f'{file}-{str(previous)}.files.tar.gz')
