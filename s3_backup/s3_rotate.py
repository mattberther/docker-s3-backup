import datetime
import fnmatch
import logging
import os

import boto3
import rotate_backups


logger = logging.getLogger(__name__)


class S3Rotator(rotate_backups.RotateBackups):
    def __init__(self, include_list=None, dry_run=False):
        self.s3_client = boto3.client('s3')
        rotation_scheme = {
            'daily': 7,
            'weekly': 4,
            'monthly': 12,
            'yearly': 'always'
        }

        super(S3Rotator, self).__init__(rotation_scheme,
                                        include_list=include_list,
                                        dry_run=dry_run)

    def __concatenate(self, items):
        items = list(items)
        if len(items) > 1:
            return ', '.join(items[:-1]) + ' and ' + items[-1]
        elif items:
            return items[0]
        else:
            return ''

    def rotate_backups(self, bucketname):
        sorted_backups = self.collect_backups(bucketname)
        if not sorted_backups:
            logger.info(f'No backups found in {bucketname}')
            return

        most_recent = sorted_backups[-1]

        backups_by_freq = self.group_backups(sorted_backups)
        self.apply_rotation_scheme(backups_by_freq, most_recent.timestamp)
        backups_to_preserve = self.find_preservation_criteria(backups_by_freq)

        deleted_files = []
        for backup in sorted_backups:
            if backup in backups_to_preserve:
                matching_periods = backups_to_preserve[backup]
                logger.info("Preserving %s (matches %s retention %s)",
                            backup.pathname, self.__concatenate(map(repr, matching_periods)),
                            "period" if len(matching_periods) == 1 else "periods")
            else:
                logger.info("Deleting %s %s ..", backup.type, backup.pathname)
                if not self.dry_run:
                    logger.debug("Marking %s for deletion.", backup.pathname)
                    deleted_files.append({'Key': backup.pathname})

        if deleted_files:
            self.s3_client.delete_objects(Bucket=bucketname, Delete={'Objects': deleted_files})

        if len(backups_to_preserve) == len(sorted_backups):
            logger.info("Nothing to do! (all backups preserved)")

    def collect_backups(self, bucketname):
        def get_key(obj): return obj['Key']
        backups = []

        objs = self.s3_client.list_objects_v2(Bucket=bucketname)['Contents']
        sorted_objs = [obj['Key'] for obj in sorted(objs, key=get_key)]

        for obj in sorted_objs:
            match = rotate_backups.TIMESTAMP_PATTERN.search(obj)
            if match:
                if self.include_list and not any(fnmatch.fnmatch(obj, p) for p in
                                                 self.include_list):
                    continue
                else:
                    backups.append(S3Backup(pathname=obj,
                                            timestamp=datetime.datetime(*(int(group, 10) for group
                                                                          in match.groups('0'))),
                                            ))

        if backups:
            logger.info(f'Found {len(backups)} timestamped backups in {bucketname}.')

        return sorted(backups)


class S3Backup(rotate_backups.Backup):

    @property
    def type(self):
        return 's3_file'
