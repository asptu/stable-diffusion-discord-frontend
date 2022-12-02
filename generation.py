import requests
import io
import base64
from PIL import Image

url = "http://127.0.0.1:7860"


async def create(prompt):

        payload = {
        "prompt": prompt,
        "width": 768,
        "height": 768,
        "steps": 20
        }

        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        r = response.json()

        for i in r['images']:

            
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

            info = response2.json().get('info')

            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            arr = io.BytesIO()
            image.save(arr, format='PNG')
            arr.seek(0)
            return arr, image, info


async def variation(prompt, img_url):

        payload = {
        "init_images": ["data:image/png;base64," + str(base64.b64encode(requests.get(img_url).content), "utf-8")],    
        "denoising_strength": 0.75,
        "prompt": prompt,
        "width": 768,
        "height": 768,
        "steps": 20
        }

        response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)

        r = response.json()

        for i in r['images']:
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

            info = response2.json().get('info')

            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            arr = io.BytesIO()
            image.save(arr, format='PNG')
            arr.seek(0)
            return arr, image, info
