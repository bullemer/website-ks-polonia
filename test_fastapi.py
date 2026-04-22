import sys
from fastapi.testclient import TestClient
sys.path.append('backend')
from app import app
client = TestClient(app)
try:
    response = client.get("/admin")
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
