#!/usr/bin/python

import datetime
import os
import string
import tarfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from glob import glob
from datetime import timedelta

# Configuration
aws_access_key = os.environ['AWS_ACCESS_KEY']
aws_secret_key = os.environ['AWS_SECRET_KEY']
aws_bucket = os.environ['AWS_S3_BUCKET']

dirs = glob('/data/*/')

# Script Configuration
today = datetime.date.today()
previous = today - timedelta(days=7)

# Establish S3 Connection
s3 = S3Connection(aws_access_key, aws_secret_key)
b = s3.get_bucket(aws_bucket)

# File Backups
for d in dirs:
    print '[FILE] Found directory ' + d
    file = d.rstrip(os.sep).split(os.sep)[::-1][0]
    out_file = os.path.join('/tmp', file + '-' + str(today) + '.files.tar.gz')

    print '[FILE] Creating archive for ' + file

    tar = tarfile.open(out_file, 'w:gz')
    tar.add(d)
    tar.close()

    print '[S3] Uploading file archive ' + file + '...'

    k = Key(b)
    k.key = file + '-' + str(today) + '.files.tar.gz'
    k.set_contents_from_filename(out_file)

    os.remove(out_file)

    print '[S3] Clearing previous file archive ' + file + '...'

    # Preserve monthly backups (Previous Month)
    if previous != str(datetime.datetime.today().year) + '-' + str(datetime.datetime.today().month) + '-1':
        # Clean up files on S3
        k = Key(b)
        k.key = file + '-' + str(previous) + '.files.tar.gz'
        b.delete_key(k)
