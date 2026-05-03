import urllib.request
import urllib.error

try:
    response = urllib.request.urlopen('http://localhost:8000/api/health')
    print(response.read().decode())
except urllib.error.URLError as e:
    print(f"Server not reachable: {e}")

