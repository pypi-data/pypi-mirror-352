""" Functions for pulling data from s3 """

import os
from functools import partial
import boto3
from botocore.client import Config
import pandas as pd
from .tools import client_connect, resource_connect, flatten_filepath, join_filepath
import io
import librosa

from bugpy.utils import multithread, add_directory_to_fileseries

def find_missing(filelist, directory) -> list:
    """ Identifies files that exist in filelist but not in directory

        :param filelist: list of files to be found
        :type filelist: pandas.Series or list
        :param directory: directory to find them in
        :return: files which exist in the filelist but not in the directory
    """

    if type(filelist) == pd.Series:
        filelist = filelist.values
    full_filelist = pd.DataFrame(filelist, columns=['s3_loc'])
    full_filelist['local'] = add_directory_to_fileseries(directory, full_filelist['s3_loc'])

    downloaded_files = [join_filepath(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(directory)) for f in fn]

    missing = set(full_filelist['local']).difference(downloaded_files)
    full_filelist = full_filelist[full_filelist['local'].isin(missing)]

    return list(full_filelist['s3_loc'])

def download_one_file(s3_filename: str, bucket: str, output: str, s3_client=None,
                      flatten_filestructure=False, reconnect=True, serial=True) -> str:
    """ Download a single file from S3

        :param s3_filename: S3 object name
        :param bucket : S3 bucket where files are hosted
        :param output: Dir to store the files
        :param s3_client: S3 client
        :type s3_client: boto3.client
        :param flatten_filestructure: determines whether directory structure is recreated or flattened
        :param reconnect: whether to attempt to create a new s3 session
        :param serial: whether this function will be run serially or in multithreaded
        :return: path of downloaded file
    """
    if reconnect or s3_client is None:
        s3_client = client_connect()

    if flatten_filestructure:
        s3_savename = flatten_filepath(s3_filename)
    else:
        folders = os.path.split(s3_filename)[0]
        if not os.path.isdir(join_filepath(output, folders)):
            os.makedirs(join_filepath(output, folders))
        s3_savename = s3_filename

    output_file = join_filepath(output, s3_savename)

    if serial:
        try:
            s3_client.download_file(
                Bucket=bucket, Key=s3_filename, Filename=output_file
            )
        except Exception as e:
            print(f"Error in downloading {bucket + '/' + s3_filename} to {output_file}")
            print(e)
    else:
        s3_client.download_file(
            Bucket=bucket, Key=s3_filename, Filename=output_file
        )

    return output_file


def _build_download_dirs(filelist, output):
    """Ensures that all directories required for the download exist.

    :param filelist: Series of file paths to be created.
    :type filelist: pandas.Series
    :param output: Root output directory.
    :type output: str
    """
    folders = filelist.str.rsplit('/', n=1).str[0].unique()
    for folder in folders:
        if not os.path.isdir(join_filepath(output, folder)):
            os.makedirs(join_filepath(output, folder))


def collect_one_from_bucket(file_location, bucket):
    """Streams a file from an S3 bucket.

    :param file_location: S3 object key.
    :type file_location: str
    :param bucket: S3 bucket name or a boto3 Bucket object.
    :type bucket: str or boto3.resources.factory.s3.Bucket
    :return: A stream of the file's contents.
    :rtype: botocore.response.StreamingBody
    """
    if type(bucket) == str:
        s3_resource = resource_connect()
        bucket = s3_resource.Bucket(bucket)

    file_object = bucket.Object(file_location)

    response = file_object.get()
    file_stream = response['Body']

    return file_stream

def stream_one_audiofile(file_location, bucket, desired_sr=None):
    """Streams an audio file from S3 and loads it with librosa.

    :param file_location: S3 key of the audio file.
    :type file_location: str
    :param bucket: S3 bucket name or Bucket object.
    :type bucket: str or boto3.resources.factory.s3.Bucket
    :param desired_sr: Desired sampling rate.
    :type desired_sr: int, optional
    :return: Tuple of waveform (as np.ndarray) and sample rate.
    :rtype: tuple
    """
    file_stream = collect_one_from_bucket(file_location, bucket)
    audio_bytes = io.BytesIO(file_stream.read())
    sr = {}
    if desired_sr is not None:
        sr['sr']=desired_sr
    audio, sr = librosa.load(audio_bytes, **sr)

    return audio, sr


def download_filelist(filelist, output_dir, aws_bucket, flatten_filestructure=False, redownload=False) -> list:
    """Downloads multiple files from an S3 bucket, optionally in parallel.

    :param filelist: List of S3 object keys to download.
    :type filelist: list
    :param output_dir: Local directory to store downloaded files.
    :type output_dir: str
    :param aws_bucket: Name of the S3 bucket.
    :type aws_bucket: str
    :param flatten_filestructure: Whether to flatten the directory structure when saving locally, defaults to False.
    :type flatten_filestructure: bool
    :param redownload: Whether to force re-download of already present files, defaults to False.
    :type redownload: bool
    :return: List of files that failed to download.
    :rtype: list
    """

    session = boto3.Session()
    client = session.client("s3", config=Config(max_pool_connections=os.cpu_count()),
                            endpoint_url=os.environ['ENDPOINT'],
                            aws_access_key_id=os.environ['API_KEY'],
                            aws_secret_access_key=os.environ['SECRET_KEY'])

    filelist = pd.Series(filelist).dropna()
    filelist = filelist.drop_duplicates()
    filelist = filelist[filelist != '']

    # The client is shared between threads
    func = partial(download_one_file, bucket=aws_bucket, output=output_dir, s3_client=client,
                   flatten_filestructure=flatten_filestructure, reconnect=False, serial=False)

    if redownload:
        files_to_download = filelist
    else:
        files_to_download = find_missing(filelist, output_dir)
        if len(filelist) > len(files_to_download):
            print(f"Some files already downloaded, downloading {len(files_to_download)} new files")
        else:
            print(f"Downloading {len(files_to_download)} new files")

    if len(files_to_download) == 0:
        return []

    if not flatten_filestructure:
        _build_download_dirs(pd.Series(files_to_download), output_dir)

    failed_downloads, _ = multithread(files_to_download,
                                      func,
                                      description="Downloading files from S3",
                                      retry=True)

    print(f"Successfully downloaded {len(files_to_download) - len(failed_downloads)} files.")

    if len(failed_downloads) > 0:
        print(f"WARNING! There were {len(failed_downloads)} failed downloads!")
        return failed_downloads

    return []
