import requests

url = "http://127.0.0.1:8000/template/delete/example"

response = requests.request("GET", url)

response = response.json()
if not response['error']:
    print(response['status'])
else:
    print(response['status'])
    exit(1)
