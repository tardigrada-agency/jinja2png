import requests

url = "http://127.0.0.1:8000/template/get/example"

response = requests.request("GET", url)
with open('example.jinja2', 'w') as f:
    f.write(response.content.decode('UTF-8'))
