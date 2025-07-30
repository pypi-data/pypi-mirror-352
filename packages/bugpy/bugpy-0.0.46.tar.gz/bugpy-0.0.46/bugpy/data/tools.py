import os
import boto3
import botocore
from bugpy.utils import get_credentials


def client_connect(connection_pool=None, cred='s3_web'):
    """ Makes a s3 connection

        :param connection_pool: connection pool size, defaults to your CPU count
        :return: s3 client
    """

    if connection_pool is None:
        connection_pool = os.cpu_count()
    s3_client = boto3.client('s3', config=botocore.client.Config(max_pool_connections=connection_pool),
                             aws_access_key_id=get_credentials(cred, 'API_KEY'),
                             aws_secret_access_key=get_credentials(cred, 'SECRET_KEY'),
                             endpoint_url=get_credentials(cred, 'ENDPOINT'))
    return s3_client


def resource_connect(cred='s3_web'):
    """ Makes a s3 connection

        :return: s3 resource
    """

    s3_client = boto3.resource('s3',
                               aws_access_key_id=get_credentials(cred, 'API_KEY'),
                               aws_secret_access_key=get_credentials(cred, 'SECRET_KEY'),
                               endpoint_url=get_credentials(cred, 'ENDPOINT'))
    return s3_client


def flatten_filepath(input_string) -> str:
    """ Replaces folder structure with _ character

        :param input_string: string to be formatted
        :return: formatted string
    """
    output_string = re.sub('/', '_', input_string)

    return output_string


def join_filepath(pathlist):
    pathlist = [x.replace('\\', '/') for x in pathlist]
    return ('/'.join(pathlist)).replace('//', '/')
