# docker-s3-backup

Simple docker container that allows the compressing of mounted folders to Amazon S3.

## Usage

```
docker run \
  --rm \
  -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY> \
  -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_KEY> \
  -e AWS_S3_BUCKET=<AWS_S3_BUCKET> \
  -e BACKUP_EXCLUDE_FILES=<FILE_LIST> \
  -v </path/to/folder/to/backup>:/data/<foldername> \
  mattberther/s3-backup
```

## Parameters
The following parameters are able to be passed to the container. In the case of a parameter separated by a colon, the left hand represents the host side and the right, the container side.

* `-e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>` - the access key used to access your S3 bucket
* `-e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>` - the secret key used to access your S3 bucket
* `-e AWS_S3_BUCKET=<AWS_S3_BUCKET>` - the name of the S3 bucket to store the backup to
* `-e BACKUP_EXCLUE_FILES=<FILE_LIST>` - a semicolon delimited list of glob-style patterns that should be excluded from the archive
* `-v </path/to/folder/to/backup>:/data/<foldername>` - one or more folders from the host that will be backed up to S3. The container's mountpoint will be used as the archive's base name. For example: mounting a folder to `<src>:/data/services-data`, will create an archive named `services-data-YYYY-MM-DD.files.tar.gz` in the configured S3 bucket.

## Versions
* **0.3.0**: Implement proper S3 rotation retaining last 7 daily, last 4 weekly, last 12 monthly, and all yearly backups
* **0.2.0**: Add ability to exclude files from backup 
* **0.1.0**: Initial commit
