import boto3, os, csv, io, re
s3=boto3.client('s3')
BUCKET_NAME=os.environ.get('BUCKET_NAME','magickvoice-pipeline-reshma')
RAW_PREFIX='raw/'; FORMATTED_PREFIX='formatted/'; ARCHIVE_PREFIX='archive/'
def normalize_phone(value):
    if value is None:return ''
    value=str(value).strip().replace('"','').strip()
    if not value:return ''
    if 'e' in value.lower():
        try:value=str(int(float(value)))
        except ValueError:return value
    if re.fullmatch(r'\d+\.0',value):value=value.split('.')[0]
    value=re.sub(r'[\s\-\(\)]','',value)
    if value.startswith('+91') and len(value)==13:return value
    if value.startswith('91') and len(value)==12:return '+'+value
    if len(value)==10 and value.isdigit():return '+91'+value
    return value
def lambda_handler(event,context):
    record=event['Records'][0]; bucket=record['s3']['bucket']['name']; key=record['s3']['object']['key']
    if not key.startswith(RAW_PREFIX):return {'statusCode':200,'message':'File is outside raw/ prefix'}
    if not key.lower().endswith('.csv'):return {'statusCode':400,'message':'Only CSV files are accepted','file':key}
    content=s3.get_object(Bucket=bucket,Key=key)['Body'].read().decode('utf-8-sig')
    rows=list(csv.reader(io.StringIO(content)))
    if not rows:raise Exception('CSV file is empty')
    headers=[str(x).strip().lower().replace('_',' ') for x in rows[0]]
    phone_index=next((i for i,x in enumerate(headers) if x in ['phone','mobile','mobile number','phone number','contact number']),None)
    if phone_index is not None:
        for row in rows[1:]:
            if phone_index<len(row):row[phone_index]=normalize_phone(row[phone_index])
    out=io.StringIO(); csv.writer(out,quoting=csv.QUOTE_MINIMAL,lineterminator='\n').writerows(rows)
    filename=key.split('/')[-1]; formatted=FORMATTED_PREFIX+filename; archive=ARCHIVE_PREFIX+filename
    s3.put_object(Bucket=bucket,Key=formatted,Body=out.getvalue().encode(),ContentType='text/csv')
    s3.copy_object(Bucket=bucket,CopySource={'Bucket':bucket,'Key':key},Key=archive); s3.delete_object(Bucket=bucket,Key=key)
    return {'statusCode':200,'message':'CSV processed successfully','formatted_file':formatted,'archived_file':archive}
