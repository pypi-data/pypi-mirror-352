from bugpy.data import upload_filelist
from bugpy.ingestion import collect_metadata
from bugpy.utils import get_credentials


def upload_recordings(db, partial_upload=True, prompt_disconnect=False):
    """ Uploads a list of recordings from local storage

        :param db: bugpy.Connection object
        :param partial_upload: Whether to tolerate a partial upload
        :param prompt_disconnect: Whether to prompt the user to disconnect from the VPN to speed up upload
        :return: list of files which failed to upload
    """
    df = collect_metadata(db)

    df['file_path'] = 'raw_data/project_'+df['project_id'].astype(str)+'/experiment_'+df['experiment_id'].astype(str)+'/'+df['file_loc']

    experiment_ids = ','.join(df['experiment_id'].astype(str).unique())
    existing = db.query(f"select file_path from recordings where experiment_id in ({experiment_ids})")
    df = df[~df['file_path'].isin(existing)]

    if prompt_disconnect:
        print("Uploading data now, for faster upload, disconnect from the VPN now.")
        input("Press enter when you are ready")

    bucket = get_credentials('s3_web', 'BUCKET')
    fails = upload_filelist(df['local_loc'],bucket, uploadnames=df['file_path'])

    if len(fails)>0 and not partial_upload:
        print(f"{len(fails)} files failed to upload - check and retry")
        return fails
    df = df[~df['file_loc'].isin(fails)]

    if prompt_disconnect:
        print("Upload complete, reconnect to the VPN")
        input("Press enter when you are ready")

    df['file_path'] = df['file_path'].str.replace('\\','/')

    db.insert(df, 'recordings')

    return fails