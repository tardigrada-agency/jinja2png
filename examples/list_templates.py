import requests

url = "http://127.0.0.1:8000/template/list"

response = requests.request("GET", url)

print('Templates:')
for template in response.json():
    print(f'    {template}')
