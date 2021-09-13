from jinja2 import Environment, FileSystemLoader
from starlette.background import BackgroundTask
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
import imgkit
import uuid
import time
import os
import re

app = FastAPI()
templates = Jinja2Templates(directory="static")

app.mount("/static", StaticFiles(directory="static"), name="static")


def delete_file(path: str):
    if not os.path.exists(path):
        os.remove(path)


def validate_template_name(template_name: str) -> dict:
    if not re.match(r'^[a-zA-Z0-9|\-_]+$', template_name):
        return {'error': True,
                'status': 'invalid filename, Only English letters, numbers and underscores are allowed',
                'template_name': template_name}
    else:
        return {'error': False,
                'status': 'filename is good :)',
                'template_name': template_name}


@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/template/delete/{template_name}')
async def delete_template(template_name: str):
    validate = validate_template_name(template_name)
    if validate['error']:
        return validate
    if not os.path.exists(f'templates/{template_name}.jinja2'):
        return {'error': True,
                'status': f'"{template_name}.jinja2" does not exist',
                'template_name': template_name}
    os.remove(f'templates/{template_name}.jinja2')
    if not os.path.exists(f'templates/{template_name}.jinja2'):
        return {'error': False,
                'status': f'"{template_name}.jinja2" successfully deleted',
                'template_name': template_name}


@app.get('/template/list')
async def list_templates():
    templates = []
    for template in os.listdir('templates/'):
        templates.append(os.path.splitext(template)[0])
    return templates


@app.get('/template/get/{template_name}')
async def get_template(template_name: str):
    validate = validate_template_name(template_name)
    if validate['error']:
        return validate
    if not os.path.exists(f'templates/{template_name}.jinja2'):
        return {'error': True,
                'status': f'"{template_name}.jinja2" does not exist',
                'template_name': template_name}
    return FileResponse(f'templates/{template_name}.jinja2')


@app.post('/template/upload/{template_name}')
async def upload_template(template_name: str, data: Request):
    data = await data.body()
    data = data.decode('UTF-8')
    validate = validate_template_name(template_name)
    if validate['error']:
        return validate
    if not os.path.exists(f'templates/{template_name}.jinja2'):
        with open(f'templates/{template_name}.jinja2', 'w') as file:
            file.write(data)
            return {'error': False,
                    'status': f'successfully saved as "{template_name}.jinja2"',
                    'template_name': template_name}
    else:
        return {'error': True,
                'status': f'"{template_name}.jinja2" already exists, please try another template name',
                'template_name': template_name}


@app.post('/template/render/{template_name}')
async def render_template(template_name: str, data: Request):
    validate = validate_template_name(template_name)
    f = open('templates/time.txt', 'w')
    f.write(f'starting {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    if validate['error']:
        return validate
    if not os.path.exists(f'templates/{template_name}.jinja2'):
        return {'error': True,
                'status': f'"{template_name}.jinja2" does not exist',
                'template_name': template_name}
    image_uuid = uuid.uuid4()
    data = await data.json()
    # shot = WebShot()
    # shot.quality = 80

    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(f'{template_name}.jinja2')
    f.write(f'env.get_template {time.strftime("%Y-%m-%d %H:%M:%S")}\n')

    # image = shot.create_pic(html=template.render(
    #     images=data['images'],
    #     texts=data['texts']
    # ), output=f'images/{image_uuid}.png')
    imgkit.from_string(template.render(
        images=data['images'],
        texts=data['texts']
    ), f'images/{image_uuid}.png')
    f.write(f'shot.create_pic ended {time.strftime("%Y-%m-%d %H:%M:%S")}\n')

    f.write(f'ended {time.strftime("%Y-%m-%d %H:%M:%S")}')
    f.close()
    return FileResponse(f'images/{image_uuid}.png', background=BackgroundTask(delete_file, f'images/{image_uuid}.png'))
