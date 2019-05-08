import boto3
import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

def is_dir(path):
    """
    :type path: str
    :rtype: bool
    """
    return path[-1] == '/'

def download_file(bucket_name, obj_key, dest_path):
    """
    :type bucket_name: str
    :type obj_key: str
    :type dest_path: str
    :rtype: bool
    """

    # meta folder in S3 will raise exceptions
    status = None
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        bucket.download_file(obj_key, dest_path)
        status = dest_path
    except Exception as e:
        # print('s3_utils/download_file: Exception: {}'.format(e))
        pass
    return status

def download_dir(bucket_name, bucket_prefix, dest_path):
    """
    :type bucket_name: str
    :type bucket_prefix: str
    :type dest_path: str
    :rtype: bool
    """

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    status = None
    try:
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)

        objs = bucket.objects.filter(Prefix = bucket_prefix)
        
        for obj in objs:
            path, file_name = os.path.split(obj.key)
            dir_path = os.path.join(dest_path, path)
	    
            print('Path: {}'.format(dir_path))
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            obj_path = os.path.join(dir_path, file_name)
            download_file(bucket_name, obj.key, obj_path)

        status = os.path.join(dest_path, bucket_prefix)
    except Exception as e:
        print('s3_utils/download_folder: Exception: {}'.format(e))

    return status
