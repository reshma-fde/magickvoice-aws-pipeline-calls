# MagickVoice AWS Pipeline

FTP/SFTP → EventBridge → FTP Watcher → S3 raw/ → Formatter → formatted/archive → Contact Upload → Contact List API → Broadcast Launcher → Broadcast API.

Region: `eu-north-1`  
Bucket: `magickvoice-pipeline-reshma`

## Lambda functions
- `magickvoice-ftp-watcher`: FTP → S3 raw/
- `magickvoice-file-formatter`: CSV normalization → formatted/ + archive/
- `magickvoice-contact-upload`: formatted CSV → Contact List API
- `magickvoice-broadcast-launcher`: header-based script selection → Broadcast API

## Security
Real credentials are intentionally excluded. Use `docs/SECRETS.md` with AWS Secrets Manager. Do not commit keys.

## Current limitations
Formatter is CSV-only. Production source should use SFTP. IAM permissions should be narrowed to least privilege. Broadcast currently creates one recipient per CSV row.
