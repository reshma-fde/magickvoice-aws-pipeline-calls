import boto3,os,json,csv,io,urllib.request,urllib.error
s3=boto3.client('s3'); secrets=boto3.client('secretsmanager')
SECRET_NAME=os.environ.get('SECRET_NAME','magickvoice/contact-api'); API_URL='https://appi.magickvoice.com/proxy/calls/bulk'
PLACEMENT_SCRIPT_ID='93dee477-4963-4e71-b5f5-a94df950924e'; SPINNY_SCRIPT_ID='26fb3c47-dbc1-463f-9abd-de0b96bc4e5f'
def norm(x):return str(x).strip().lower().replace('_',' ').replace('-',' ')
def choose(headers):
    h={norm(x) for x in headers}; p={'institute name','student name','company name','role','package','location','skills'}; s={'car id','brand','model','year'}
    if p.intersection(h):return PLACEMENT_SCRIPT_ID,'Placement'
    if s.intersection(h):return SPINNY_SCRIPT_ID,'Spinny Catalog'
    return None,None
def lambda_handler(event,context):
    bucket=event.get('bucket'); key=event.get('key');
    if not bucket or not key:raise Exception('bucket and key are required')
    content=s3.get_object(Bucket=bucket,Key=key)['Body'].read().decode('utf-8-sig'); rows=list(csv.DictReader(io.StringIO(content)))
    if not rows:return {'statusCode':200,'message':'No recipients'}
    script,campaign=choose(list(rows[0].keys())); print('Headers:',list(rows[0].keys())); print('Selected campaign:',campaign); print('Script ID:',script)
    if not script:raise Exception('No matching AI script was found for this CSV')
    cfg=json.loads(secrets.get_secret_value(SecretId=SECRET_NAME)['SecretString']); recipients=[]
    for row in rows:
        phone=(row.get('phone') or row.get('mobile') or row.get('mobile number') or '').strip()
        if phone:recipients.append({'phone':phone,'language':'en','prompt_variables':{'recipient_name':row.get('customer_name') or row.get('student_name') or row.get('name') or ''}})
    if not recipients:raise Exception('No valid recipients found')
    payload={'prompt_template_id':script,'ai_pipeline':'platinum','caller_id':'+918065480974','caller_ids':['+918065480974'],'config':{'language':'en'},'enable_recording':False,'hangup_on_machine':False,'machine_detection':False,'recipients':recipients}
    req=urllib.request.Request(API_URL,data=json.dumps(payload).encode(),method='POST'); req.add_header('Content-Type','application/json'); req.add_header('X-Platform-Key',cfg['platform_key']); req.add_header('X-Tenant-Id',cfg['tenant_id']); req.add_header('X-Account-Id',cfg['account_id'])
    try:
        with urllib.request.urlopen(req,timeout=30) as resp:status=resp.status; result=resp.read().decode()
    except urllib.error.HTTPError as e:print('Broadcast API error:',e.code,e.read().decode(errors='replace'));raise
    print('Broadcast API status:',status); print('Broadcast API response:',result); return {'statusCode':status,'campaign':campaign,'script_id':script,'recipient_count':len(recipients),'response':result}
