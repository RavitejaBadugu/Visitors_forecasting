from preprocess import create_reservations_table,create_cuisine_geo_tables
import boto3
import os
role_arn=os.environ['Rolearn'].strip()
bucket_name=os.environ['BucketName'].strip()

def get_bucket():
    sts_client = boto3.client('sts')
    assumed_role_object=sts_client.assume_role(
                                                RoleArn=role_arn,
                                                RoleSessionName="AssumeRoleSession1"
                                            )
    credentials=assumed_role_object['Credentials']
    s3=boto3.resource(
                                's3',
                                aws_access_key_id=credentials['AccessKeyId'],
                                aws_secret_access_key=credentials['SecretAccessKey'],
                                aws_session_token=credentials['SessionToken'],
    )
    bucket = s3.Bucket(name=bucket_name)
    return bucket

def get_model(base_path):
    bucket=get_bucket()
    bucket.download_file("lstm_2_dense_1.h5",f'{base_path}/lstm_2_dense_1.h5')
    bucket.download_file("predictive_features,.pkl",f'{base_path}/predictive_features,.pkl')
    bucket.download_file("scaler_lstm_0.001_2.pkl",f'{base_path}/scaler_lstm_0.001_2.pkl')

def create_new_tables():
    create_reservations_table('air_reserve.csv','hpg_reserve.csv','store_id_relation.csv')
    create_cuisine_geo_tables("air_store_info.csv",'hpg_store_info.csv','store_id_relation.csv')

if __name__ == '__main__':
    #Below authetication code is from documentation
    bucket=get_bucket()
    bucket.download_file("air_reserve.csv",'air_reserve.csv')
    bucket.download_file("air_visit_data.csv",'air_visit_data.csv')
    bucket.download_file("air_store_info.csv",'air_store_info.csv')
    bucket.download_file("hpg_reserve.csv",'hpg_reserve.csv')
    bucket.download_file("hpg_store_info.csv",'hpg_store_info.csv')
    bucket.download_file("date_info.csv",'date_info.csv')
    bucket.download_file("store_id_relation.csv",'store_id_relation.csv')
    bucket.download_file("sample_submission.csv",'sample_submission.csv')
    