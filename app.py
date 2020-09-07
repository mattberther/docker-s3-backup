#!/usr/bin/python

import datetime
import os
import string
import tarfile
import fnmatch

import boto3
from botocore.exceptions import ClientError

from glob import glob
from datetime import timedelta

# Configuration
aws_bucket = os.environ['AWS_S3_BUCKET']

exclude_files = []
if os.environ.get('BACKUP_EXCLUDE_FILES'):
    exclude_files = os.environ.get('BACKUP_EXCLUDE_FILES').split(';')

dirs = glob('/data/*/')

# Script Configuration
today = datetime.date.today()

# Establish S3 Connection
s3_client = boto3.client('s3')


def should_include(tarinfo):
    for x in exclude_files:
        if fnmatch.fnmatch(tarinfo.name, x):
            print(f'[FILE] Excluding {tarinfo.name} based on filter: {x}')
            return None

    return tarinfo


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, 'w:gz') as tar:
        tar.add(source_dir, filter=should_include)
        tar.close()


def upload_s3(tarfile):
    filename = os.path.basename(tarfile)
    print(f'[S3] Uploading file archive {tarfile}...')
    try:
        resp = s3_client.upload_file(tarfile, aws_bucket, filename)
    except ClientError as e:
        logging.error(e)


def cleanup_s3(folder):
    print(f'[S3] Clearing previous file archive {file}...')

    previous = today - timedelta(days=7)
    # Preserve monthly backups (Previous Month)
    if previous != str(datetime.datetime.today().year) + '-' + str(datetime.datetime.today().month) + '-1':
        # Clean up files on S3
        s3_client.delete_object(Bucket=aws_bucket, Key=f'{file}-{str(previous)}.files.tar.gz')


for x in exclude_files:
    print(f'[FILE] Excluding patten {x}')

for d in dirs:
    print(f'[FILE] Found directory {d}')
    file = d.rstrip(os.sep).split(os.sep)[::-1][0]
    filename = f'{file}-{str(today)}.files.tar.gz'
    out_file = os.path.join('/tmp', filename)

    print(f'[FILE] Creating archive for {file}')
    make_tarfile(out_file, d)

    upload_s3(out_file)
    cleanup_s3(file)
    os.remove(out_file)
