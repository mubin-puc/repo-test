import boto3
import gzip
import base64
import json
import urllib3
from datetime import datetime

http = urllib3.PoolManager()

OPENSEARCH_ENDPOINT = "vpc-fpf-monitoring-abgdrtmctrnu7unjguc3jxh7lq.us-east-1.es.amazonaws.com"
INDEX_PREFIX = "rdsosmetrics"

headers = {
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    decoded_data = base64.b64decode(event['awslogs']['data'])
    uncompressed_data = gzip.decompress(decoded_data)
    payload = json.loads(uncompressed_data)

    if payload.get('messageType') == 'CONTROL_MESSAGE':
        print("Control message received")
        return {'status': 'control message ignored'}

    bulk_payload = ""
    for log_event in payload['logEvents']:
        try:
            source = json.loads(log_event['message'])
        except json.JSONDecodeError:
            print(f"Skipping unparseable log: {log_event['message']}")
            continue

        timestamp = datetime.utcfromtimestamp(log_event['timestamp'] / 1000.0)
        index_name = f"{INDEX_PREFIX}-{timestamp.strftime('%Y.%m.%d')}"

        source['@timestamp'] = timestamp.isoformat()
        source['@id'] = log_event['id']
        source['@log_group'] = payload['logGroup']
        source['@log_stream'] = payload['logStream']

        action = {
            "index": {
                "_index": index_name,
                "_id": log_event['id']
            }
        }

        bulk_payload += json.dumps(action) + "\n" + json.dumps(source) + "\n"

    if bulk_payload:
        url = f"https://{OPENSEARCH_ENDPOINT}/_bulk"
        r = http.request(
            "POST",
            url,
            body=bulk_payload.encode('utf-8'),
            headers=headers
        )

        print("OpenSearch response status:", r.status)
        if r.status >= 200 and r.status < 300:
            return {'status': 'success', 'bulk_status': r.status}
        else:
            print("Failed to post to OpenSearch:", r.data.decode())
            return {'status': 'error', 'code': r.status, 'body': r.data.decode()}
    else:
        return {'status': 'no valid logs to send'}
