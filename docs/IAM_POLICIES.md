# IAM Policy Notes

Watcher: CloudWatch logs + Secrets Manager GetSecretValue + S3 write/read-check for raw/.
Formatter: S3 GetObject raw/, PutObject formatted/archive/, DeleteObject raw/, logs.
Contact Upload: S3 GetObject formatted/, Secrets Manager GetSecretValue, Lambda InvokeFunction for broadcast, logs.
Broadcast: S3 GetObject formatted/, Secrets Manager GetSecretValue, logs.

Broad policies were used during troubleshooting; narrow them before production.
