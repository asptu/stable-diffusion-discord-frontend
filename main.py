import requests
import io
import base64
from PIL import Image

url = "http://127.0.0.1:7860"


async def create(prompt):

    # if img_url != '':

    #     # pil_image = Image.open(filename)

    #     # def pil_to_base64(pil_image):
    #     #     with io.BytesIO() as stream:
    #     #         pil_image.save(stream, "PNG", pnginfo=None)
    #     #         base64_str = str(base64.b64encode(stream.getvalue()), "utf-8")
    #     #         return "data:image/png;base64," + base64_str

    #     payload = {
    #     "init_images": ["data:image/png;base64," + str(base64.b64encode(requests.get(img_url).content), "utf-8")],    
    #     "denoising_strength": 0.5,
    #     "prompt": prompt,
    #     "width": 768,
    #     "height": 768,
    #     "steps": 20
    #     }

    #     response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)

    #     r = response.json()

    #     for i in r['images']:
    #         image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
    #         image.save('output.png')

    # else:

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


            string = info[info.rfind('\n'):].replace('\n','').replace(' ','').split(',')
            steps = string[0].split(':')
            sampler = string[1].split(':')
            cfg = string[2].replace('scale', '').split(':')
            seed = string[3].split(':')
            size = string[4].split(':')
            height = size[1][size[1].rfind('x'):].replace('x','')
            width = size[1].split('x')
            width = width[0]
            model = string[5].replace('hash', '').split(':')
            denoising = string[7].replace('strength','').split(':')

            json_format = {
                "steps": steps[1],
                "sampler_name": sampler[1],
                "seed": seed[1],
                "cfg_scale": cfg[1],
                "width": width,
                "height": height,
                "model": model[1],
                "denoising_strength": denoising[1]
                }

            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            arr = io.BytesIO()
            image.save(arr, format='PNG')
            arr.seek(0)
            return arr, image, json_format


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

            string = info[info.rfind('\n'):].replace('\n','').replace(' ','').split(',')
            steps = string[0].split(':')
            sampler = string[1].split(':')
            cfg = string[2].replace('scale', '').split(':')
            seed = string[3].split(':')
            size = string[4].split(':')
            height = size[1][size[1].rfind('x'):].replace('x','')
            width = size[1].split('x')
            width = width[0]
            model = string[5].replace('hash', '').split(':')
            denoising = string[7].replace('strength','').split(':')

            json_format = {
                "steps": steps[1],
                "sampler_name": sampler[1],
                "seed": seed[1],
                "cfg_scale": cfg[1],
                "width": width,
                "height": height,
                "model": model[1],
                "denoising_strength": denoising[1]
                }

            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            arr = io.BytesIO()
            image.save(arr, format='PNG')
            arr.seek(0)
            return arr, image, json_format
