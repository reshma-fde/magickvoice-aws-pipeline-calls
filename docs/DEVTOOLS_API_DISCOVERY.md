# Chrome DevTools API Discovery

Chrome → Inspect → Network → Fetch/XHR. Perform the operation in MagickVoice, then inspect the request URL, method, headers, payload and response.

Contact List: POST `https://appi.magickvoice.com/contact-lists`
Broadcast: POST `https://appi.magickvoice.com/proxy/calls/bulk`

Observed auth headers: `X-Platform-Key`, `X-Tenant-Id`, `X-Account-Id`. Contact upload also uses `x-mgkvc-originator: magickvoice-customer-ui`.

Sensitive values are stored in AWS Secrets Manager.
