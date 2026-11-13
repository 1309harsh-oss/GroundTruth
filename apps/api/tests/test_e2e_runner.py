import urllib.request
import urllib.parse
import json
import io
from PIL import Image

API = 'http://localhost:8000'
WEB = 'http://localhost:3000'

print('====================================================')
print('   GROUNDTRUTH END-TO-END AUTOMATED TEST SUITE      ')
print('====================================================')

# TEST 1: Frontend Server
print('\n[TEST 1] Verifying Frontend Web Server...')
req_web = urllib.request.urlopen(WEB)
assert req_web.getcode() == 200
print('  PASS: Frontend running on port 3000 (HTTP 200 OK)')

# TEST 2: Backend Health
print('\n[TEST 2] Verifying Backend Health API...')
req_health = urllib.request.urlopen(f'{API}/health')
health_data = json.loads(req_health.read())
assert health_data['status'] == 'ok'
assert health_data['project'] == 'GroundTruth'
print(f"  PASS: Backend running on port 8000 (Status: {health_data['status']}, Version: {health_data['version']})")

# TEST 3: User Authentication & JWT Issuance
print('\n[TEST 3] Testing Authentication & RBAC JWT Generation...')
login_data = json.dumps({'email': 'worker@groundtruth.local', 'password': 'password123'}).encode('utf-8')
req_auth = urllib.request.Request(f'{API}/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
resp_auth = urllib.request.urlopen(req_auth)
token_data = json.loads(resp_auth.read())
token = token_data['access_token']
assert token_data['role'] == 'SUBMITTER'
print(f"  PASS: Submitter logged in successfully (Role: {token_data['role']})")

# TEST 4: Evidence Submission & Server-Side SHA-256 Hashing
print('\n[TEST 4] Testing Evidence Upload with Server-Side Cryptographic Hash...')
img = Image.new('RGB', (800, 600), color=(40, 120, 200))
buf = io.BytesIO()
img.save(buf, format='JPEG')
img_bytes = buf.getvalue()

boundary = '----GroundTruthBoundary987654321'
body = []
body.extend([
    f'--{boundary}'.encode(),
    b'Content-Disposition: form-data; name="milestone_id"',
    b'',
    b'seed',
    f'--{boundary}'.encode(),
    b'Content-Disposition: form-data; name="category"',
    b'',
    b'REBAR_INSPECTION',
    f'--{boundary}'.encode(),
    b'Content-Disposition: form-data; name="notes"',
    b'',
    b'Live test rebar inspection photo',
    f'--{boundary}'.encode(),
    b'Content-Disposition: form-data; name="capture_latitude"',
    b'',
    b'28.6140',
    f'--{boundary}'.encode(),
    b'Content-Disposition: form-data; name="capture_longitude"',
    b'',
    b'77.2091',
    f'--{boundary}'.encode(),
    b'Content-Disposition: form-data; name="file"; filename="test_rebar.jpg"',
    b'Content-Type: image/jpeg',
    b'',
    img_bytes,
    f'--{boundary}--'.encode(),
    b''
])
payload = b'\r\n'.join(body)
req_upload = urllib.request.Request(
    f'{API}/api/v1/evidence/submit',
    data=payload,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
resp_upload = urllib.request.urlopen(req_upload)
ev_record = json.loads(resp_upload.read())
ev_id = ev_record['id']
recorded_hash = ev_record['sha256_hash']
print(f'  PASS: Evidence created (ID: {ev_id})')
print(f'        Server Computed SHA-256: {recorded_hash}')

# TEST 5: Cryptographic Integrity Verification (Byte Re-Hashing)
print('\n[TEST 5] Testing Cryptographic Integrity Verification Endpoint...')
req_verify = urllib.request.urlopen(f'{API}/api/v1/evidence/verify/{ev_id}')
verify_data = json.loads(req_verify.read())
assert verify_data['is_valid'] is True
assert verify_data['status'] == 'INTEGRITY_VERIFIED'
assert verify_data['computed_sha256'] == recorded_hash
print(f"  PASS: Status -> {verify_data['status']}")
print(f"        Computed Hash == Stored Hash: {verify_data['is_valid']}")
print(f"        Result Message: {verify_data['message']}")

# TEST 6: Human Review Decision Workflow
print('\n[TEST 6] Testing Authorized Human Review Decision...')
review_payload = json.dumps({
    'decision': 'APPROVED',
    'reason': 'Verified rebar spacing adheres to MORTH Section 1600'
}).encode('utf-8')
req_review = urllib.request.Request(
    f'{API}/api/v1/evidence/review/{ev_id}',
    data=review_payload,
    headers={'Content-Type': 'application/json'}
)
resp_review = urllib.request.urlopen(req_review)
review_res = json.loads(resp_review.read())
assert review_res['decision'] == 'APPROVED'
print(f"  PASS: Review decision recorded: {review_res['decision']}")

# TEST 7: Evidence Detail & Audit Ledger
print('\n[TEST 7] Testing Evidence Detail, Reviews & Audit Trail...')
req_detail = urllib.request.urlopen(f'{API}/api/v1/evidence/detail/{ev_id}')
detail_data = json.loads(req_detail.read())
assert len(detail_data['reviews']) >= 1
assert len(detail_data['audit_history']) >= 1
print('  PASS: Retrieved full evidence detail!')
print(f"        Total Reviews in history: {len(detail_data['reviews'])}")
print(f"        Total Audit Events logged: {len(detail_data['audit_history'])}")

print('\n====================================================')
print('   ALL 7 END-TO-END SYSTEM INTEGRATION TESTS PASSED ')
print('====================================================')

