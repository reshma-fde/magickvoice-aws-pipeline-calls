import boto3,os,json,urllib.request,urllib.error,uuid
s3=boto3.client('s3'); secrets=boto3.client('secretsmanager'); lambda_client=boto3.client('lambda')
BUCKET_NAME=os.environ['BUCKET_NAME']; SECRET_NAME=os.environ['SECRET_NAME']; API_BASE_URL=os.environ['API_BASE_URL'].rstrip('/'); API_ENDPOINT=os.environ.get('API_ENDPOINT','/contact-lists'); BROADCAST_FUNCTION_NAME=os.environ.get('BROADCAST_FUNCTION_NAME','magickvoice-broadcast-launcher')
def multipart(filename,data,name):
    b='----MagickVoiceBoundary'+uuid.uuid4().hex
    body=(f'--{b}\r\nContent-Disposition: form-data; name="name"\r\n\r\n{name}\r\n--{b}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: text/csv\r\n\r\n').encode()+data+f'\r\n--{b}--\r\n'.encode(); return b,body
def lambda_handler(event,context):
    r=event['Records'][0]; bucket=r['s3']['bucket']['name']; key=r['s3']['object']['key']
    if not key.startswith('formatted/') or not key.lower().endswith('.csv'):return {'statusCode':200,'message':'Ignored object'}
    cfg=json.loads(secrets.get_secret_value(SecretId=SECRET_NAME)['SecretString']); data=s3.get_object(Bucket=bucket,Key=key)['Body'].read(); filename=key.split('/')[-1]; name=os.path.splitext(filename)[0]; boundary,body=multipart(filename,data,name)
    req=urllib.request.Request(API_BASE_URL+API_ENDPOINT,data=body,method='POST'); req.add_header('Content-Type',f'multipart/form-data; boundary={boundary}'); req.add_header('X-Platform-Key',cfg['platform_key']); req.add_header('X-Tenant-Id',cfg['tenant_id']); req.add_header('X-Account-Id',cfg['account_id']); req.add_header('x-mgkvc-originator','magickvoice-customer-ui')
    try:
        with urllib.request.urlopen(req,timeout=30) as resp: status=resp.status; response=resp.read().decode()
    except urllib.error.HTTPError as e: print('Contact API error:',e.code,e.read().decode(errors='replace')); raise
    print('Contact API status:',status); print('Contact API response:',response)
    if status not in (200,201):raise Exception('Contact API failed')
    payload={'source':'magickvoice-contact-upload','bucket':bucket,'key':key,'contact_list_response':response}
    lambda_client.invoke(FunctionName=BROADCAST_FUNCTION_NAME,InvocationType='Event',Payload=json.dumps(payload).encode()); print('Broadcast Launcher invoked')
    return {'statusCode':status,'message':'Contact list uploaded successfully'}
