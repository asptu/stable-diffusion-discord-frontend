import requests
import io
import base64
from PIL import Image, PngImagePlugin

url = "http://127.0.0.1:7860"


async def create(prompt, neg_prompt):
    
        payload = {
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "width": 512,
        "height": 512,
        "steps": 20
        }

        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        r = response.json()

        for i in r['images']:

            
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

            info = response2.json().get("info")

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))


            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            arr = io.BytesIO()
            image.save(arr, format='PNG', pnginfo=pnginfo)
            arr.seek(0)
            return arr, image, info


async def variation(prompt, img_url):

        payload = {
        "init_images": ["data:image/png;base64," + str(base64.b64encode(requests.get(img_url).content), "utf-8")],    
        "denoising_strength": 0.75,
        "prompt": prompt,
        "width": 512,
        "height": 512,
        "steps": 20
        }

        response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)

        r = response.json()

        for i in r['images']:
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

            info = response2.json().get("info")
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))

            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            arr = io.BytesIO()
            image.save(arr, format='PNG', pnginfo=pnginfo)
            arr.seek(0)
            return arr, image, info

async def createadv(prompt, neg_prompt, int_image, steps, seed, cfg, width, height, model, sampler_name, denoising_strength):

    payload = {
        "init_images": ["data:image/png;base64," + str(base64.b64encode(requests.get(int_image).content), "utf-8")],    
        "denoising_strength": denoising_strength,
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "seed": seed,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg,
        "sampler_index": sampler_name,
        }

    print(model)


    option_payload = {
        "sd_model_checkpoint": "Anything-V3.0-pruned.ckpt [2700c435]",
    }

    response3 = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)

async def upscale(image_url):
    
    payload = {
    "upscaling_resize": 2,
    "upscaler_1": "lollypop",
    "upscaler_2": "None",
    "image": "data:image/png;base64," + str(base64.b64encode(requests.get(image_url).content), "utf-8")
    }

    response = requests.post(url=f'{url}/sdapi/v1/extra-single-image', json=payload)

    i = response.json()
    image = Image.open(io.BytesIO(base64.b64decode(i['image'].split(",",1)[0])))
    arr = io.BytesIO()
    image.save(arr, format='PNG')
    arr.seek(0)


    return arr, image
