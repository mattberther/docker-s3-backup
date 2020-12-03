import datetime
import fnmatch
import getopt
import logging
import os
import string
import sys
import tarfile

import boto3
from botocore.exceptions import ClientError

from glob import glob
from datetime import timedelta

from .s3_rotate import S3Rotator

# Configuration
aws_bucket = os.environ['AWS_S3_BUCKET']

exclude_files = []
if os.environ.get('BACKUP_EXCLUDE_FILES'):
    exclude_files = os.environ.get('BACKUP_EXCLUDE_FILES').split(';')

dirs = glob('/data/*/')

logger = logging.getLogger(__name__)

# Script Configuration
today = datetime.date.today()

# Establish S3 Connection
s3_client = boto3.client('s3')


def should_include(tarinfo):
    for x in exclude_files:
        if fnmatch.fnmatch(tarinfo.name, x):
            logger.debug(f'[FILE] Excluding {tarinfo.name} based on filter: {x}')
            return None

    return tarinfo


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, 'w:gz') as tar:
        tar.add(source_dir, filter=should_include)
        tar.close()


def upload_s3(tarfile):
    filename = os.path.basename(tarfile)
    logger.info(f'[S3] Uploading file archive {tarfile}...')
    try:
        resp = s3_client.upload_file(tarfile, aws_bucket, filename)
    except ClientError as e:
        logging.error(e)


def main():
    dry_run = False

    options, arguments = getopt.getopt(sys.argv[1:], 'n', ['dry-run'])
    for option, value in options:
        if option in ('-n', '--dry-run'):
            logger.info(f'Performing a dry run (because of {option})')
            dry_run = True

    for x in exclude_files:
        logger.info(f'[FILE] Excluding patten {x}')

    for d in dirs:
        logger.info(f'[FILE] Found directory {d}')
        folder = d.rstrip(os.sep).split(os.sep)[::-1][0]
        filename = f'{folder}-{str(today)}.files.tar.gz'
        out_file = os.path.join('/tmp', filename)

        logger.info(f'[FILE] Creating archive for {folder}')
        make_tarfile(out_file, d)

        upload_s3(out_file)
        S3Rotator(include_list=[f'{folder}-*.files.tar.gz'],
                  dry_run=dry_run).rotate_backups(aws_bucket)
        os.remove(out_file)


if __name__ == "__main__":
    main()
