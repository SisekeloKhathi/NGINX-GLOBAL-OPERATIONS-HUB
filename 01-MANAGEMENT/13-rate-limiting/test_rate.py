import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_request(i):
    try:
        r = requests.get('http://localhost:8094/', timeout=2)
        return f"Request {i}: {r.status_code}"
    except Exception as e:
        return f"Request {i}: ERROR - {str(e)}"

# Send 15 requests concurrently
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(make_request, i) for i in range(15)]
    for future in as_completed(futures):
        print(future.result())
