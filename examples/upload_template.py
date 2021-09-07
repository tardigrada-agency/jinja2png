import requests

url = "http://127.0.0.1:8000/template/upload/testik"

# Reading template file
with open('upload_template.py', 'r') as f:
    template = f.read()

payload = template
headers = {
  'Content-Type': 'text/plain'
}

response = requests.request("POST", url, headers=headers, data=payload)
response = response.json()

# Checking if error
if not response['error']:
    print(response['status'])
else:
    print(response['status'])
    exit(1)
