import boto3,os,io,json
from ftplib import FTP
s3=boto3.client('s3'); secrets=boto3.client('secretsmanager')
BUCKET_NAME=os.environ['BUCKET_NAME']; SECRET_NAME=os.environ['SECRET_NAME']; RAW_PREFIX=os.environ.get('RAW_PREFIX','raw/')
def lambda_handler(event,context):
    cfg=json.loads(secrets.get_secret_value(SecretId=SECRET_NAME)['SecretString']); ftp=FTP(); processed=[]
    try:
        ftp.connect(cfg['ftp_host'],int(cfg.get('ftp_port',21)),timeout=30); ftp.login(cfg['ftp_username'],cfg['ftp_password']); print('FTP connection successful'); ftp.cwd(cfg['ftp_folder']); print('Current FTP directory:',ftp.pwd()); files=ftp.nlst(); print('Files found:',files)
        for filename in files:
            if filename in ('.','..'):continue
            key=RAW_PREFIX+filename
            try:s3.head_object(Bucket=BUCKET_NAME,Key=key); print('Already exists in S3. Skipping...'); continue
            except s3.exceptions.ClientError as e:
                if e.response.get('Error',{}).get('Code') not in ('404','NoSuchKey'):raise
            buf=io.BytesIO(); ftp.retrbinary('RETR '+filename,buf.write); buf.seek(0); s3.put_object(Bucket=BUCKET_NAME,Key=key,Body=buf.getvalue()); processed.append(filename); print('Uploaded:',key)
        return {'statusCode':200,'processed':processed}
    finally:
        try:ftp.quit()
        except Exception:pass
        print('FTP connection closed')
