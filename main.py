from jinja2 import Environment, FileSystemLoader
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from htmlwebshot import WebShot
import uuid
import os
import re

app = FastAPI()


def delete_file(path: str):
    os.remove(path)


def check_name(template_name: str) -> str:
    if not template_name:
        return 'template_name cannot be empty'
    elif not re.match(r'^[a-zA-Z0-9|\-_]+$', template_name):
        return 'invalid filename, valid regex ^[a-zA-Z0-9|-_]+$'
    else:
        return ''


@app.get('/', response_class=HTMLResponse)
async def read_root():
    return '<h1>Jinja2png by Yan Khachko (<a href="https://slnk.icu/">slnk.icu</a>)</h1>'


@app.get('/template/delete/{template_name}')
async def delete_template(template_name: str):
    check = check_name(template_name)
    if check:
        return {'error': True,
                'status': check,
                'template_name': template_name}
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
    check = check_name(template_name)
    if check:
        return {'error': True,
                'status': check,
                'template_name': template_name}
    if not os.path.exists(f'templates/{template_name}.jinja2'):
        return {'error': True,
                'status': f'"{template_name}.jinja2" does not exist',
                'template_name': template_name}
    return FileResponse(f'templates/{template_name}.jinja2')


@app.post('/template/upload/{template_name}')
async def upload_template(template_name: str, data: Request):
    data = await data.body()
    data = data.decode('UTF-8')
    check = check_name(template_name)
    if check:
        return {'error': True,
                'status': check,
                'template_name': template_name}
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
    check = check_name(template_name)
    if check:
        return {'error': True,
                'status': check,
                'template_name': template_name}
    if not os.path.exists(f'templates/{template_name}.jinja2'):
        return {'error': True,
                'status': f'"{template_name}.jinja2" does not exist',
                'template_name': template_name}
    image_uuid = uuid.uuid4()
    data = await data.json()
    shot = WebShot()
    shot.quality = 100

    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(f'{template_name}.jinja2')

    image = shot.create_pic(html=template.render(
        images=data['images'],
        texts=data['texts']
    ), output=f'images/{image_uuid}.png')

    return FileResponse(image, background=BackgroundTask(delete_file, image))
