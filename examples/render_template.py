from io import open as iopen
import requests
import base64
import json


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


url = "http://127.0.0.1:8000/template/render/example"

# Values to pass to the template
payload = json.dumps({
    "texts": [
        "Elon Musk: some quote",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    ],
    "images": [
        f"data:image/jpeg;base64,{get_base64_encoded_image('./example_image.jpg')}"
    ]
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

# Saving response
with iopen('example_rendered_image.png', 'wb') as file:
  file.write(response.content)
