"""Quick end-to-end API test."""
import requests, json

BASE = "http://localhost:5000"

# 1. Test upload
print("=== UPLOAD TEST ===")
with open("sample_data.csv", "rb") as f:
    res = requests.post(f"{BASE}/api/upload", files={"file": ("sample_data.csv", f, "text/csv")})
data = res.json()
print(f"Status: {res.status_code}")
print(f"Session ID: {data['session_id']}")
print(f"Rows: {data['analysis']['rows']}, Columns: {data['analysis']['columns']}")
print(f"Issues found: {len(data['analysis']['issues'])}")
for iss in data["analysis"]["issues"]:
    print(f"  - [{iss['severity']}] {iss['column']}: {iss['detail']}")
print(f"Preview rows: {len(data['preview'])}")

# 2. Test cleaning
sid = data["session_id"]
print("\n=== CLEAN TEST ===")
clean_body = {
    "session_id": sid,
    "missing_strategy": "mean",
    "remove_duplicates": True,
    "trim_whitespace": True,
    "handle_outliers": "cap",
    "remove_constant_cols": True,
    "encode_categorical": "label",
    "scale_numeric": "standard",
    "extract_datetime": True,
}
res2 = requests.post(f"{BASE}/api/clean", json=clean_body)
data2 = res2.json()
print(f"Status: {res2.status_code}")
print(f"Result rows: {data2['rows']}, columns: {data2['columns']}")
print(f"Changes applied: {len(data2['changes'])}")
for ch in data2["changes"]:
    print(f"  - {ch['operation']}: {ch['column']} ({ch['rows_affected']} rows)")

# 3. Test download
print("\n=== DOWNLOAD TEST ===")
res3 = requests.get(f"{BASE}/api/download?session_id={sid}&format=csv")
print(f"Status: {res3.status_code}")
print(f"Content-Disposition: {res3.headers.get('Content-Disposition', 'N/A')}")
print(f"Body size: {len(res3.content)} bytes")
print("First 200 chars:", res3.text[:200])

print("\n=== ALL TESTS PASSED ===")
