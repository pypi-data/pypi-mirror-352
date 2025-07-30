""" Functions for uploading files to s3 """
from bugpy.utils import multithread, multiprocess, get_credentials
from botocore.exceptions import ClientError
from botocore.config import Config
from functools import partial
import pandas as pd
import boto3
import os


def upload_one_file(name_tuple: (str,str), bucket: str, s3_client=None, reconnect=True, s3_label='s3_web', force=False) -> None:
    """ Upload a file to an S3 bucket

        :param name_tuple: A tuple of (file_location, object_name), where file_location is current location of
        file to upload, object_name is intended name in S3
        :param bucket: Bucket to upload to
        :param s3_client: established s3 connection, autoconnects if None, defaults to None
        :param reconnect: Whether to attempt to create a new s3 session
        :param s3_label: the name of the credential group for s3 connection
        :type reconnect: bool

    """
    if reconnect or s3_client is None:
        session = boto3.Session()
        s3_client = session.client("s3", config=Config(max_pool_connections=os.cpu_count()),
                                   endpoint_url=get_credentials(s3_label,'ENDPOINT'),
                                   aws_access_key_id=get_credentials(s3_label,'API_KEY'),
                                   aws_secret_access_key=get_credentials(s3_label,'SECRET_KEY'))

    filename, object_name = name_tuple

    if not force:
        try:
            s3_client.head_object(Bucket=bucket, Key=object_name)
            return object_name
        except ClientError:
            pass

    try:
        s3_client.upload_file(
            filename, bucket, object_name
        )
    except Exception as e:
        print(f"Error in uploading {filename} to {bucket + '/' + object_name}")
        print(e)
    return object_name


def upload_filelist(filelist, aws_bucket, upload_dir=None, uploadnames=None, retry_attempts=50, retry=True, s3_label='s3_web', force_reupload=False) -> list:
    """ Uploads a list of local files

        :param filelist: iterable of image names in local storage to be uploaded
        :param aws_bucket: name of S3 bucket where images are hosted
        :param upload_dir: dir to store the images, optional
        :param uploadnames: list of directory locations/names of the uploaded images
        :param retry_attempts: number of times to retry uploads
        :param retry: retries failed uploads one time
        :param s3_label: the name of the credential group for s3 connection
        :param force_reupload: whether to forcably reupload data if already uploaded
        :return: list of files which failed to upload
    """

    config = Config(
        retries=dict(
            max_attempts=retry_attempts
        ),
        max_pool_connections=os.cpu_count()
    )
    session = boto3.Session()
    client = session.client("s3", config=config,
                            endpoint_url=get_credentials(s3_label,'ENDPOINT'),
                            aws_access_key_id=get_credentials(s3_label,'API_KEY'),
                            aws_secret_access_key=get_credentials(s3_label,'SECRET_KEY'))

    filelist = pd.Series(filelist).dropna()

    if uploadnames is None and upload_dir is None:
        print("Please supply one of: upload_dir, uploadnames")

    if uploadnames is None and upload_dir is not None:
        uploadnames = filelist.apply(lambda col: os.path.join(upload_dir, os.path.basename(col)))

    func = partial(upload_one_file, bucket=aws_bucket, s3_client=client, reconnect=False, s3_label=s3_label, force=force_reupload)

    if len(filelist) == 0:
        return []

    uploadnames = uploadnames.str.replace('\\', '/', regex=False)

    inputs = pd.Series(zip(filelist, uploadnames))

    failed_uploads, successes = multithread(inputs, func, description="Uploading images to S3", retry=retry)

    print(f"Uploaded {len(filelist) - len(failed_uploads)} images with  {len(failed_uploads)} failures.")

    return failed_uploads
