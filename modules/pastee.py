import requests
import json

with open('settings.json') as settings:
    data = json.load(settings)
    pe_token = data['PE_TOKEN']

    pe_headers = {
    'Content-Type': 'application/json',
    'X-Auth-Token': pe_token,
    }

async def pastee_post(prompt, pnginfo):

        data = {
            "description":prompt[:12] + (prompt[12:] and '...'),"sections":[{"name":prompt[:12] + (prompt[12:] and '...'),"syntax":"autodetect","contents":"Prompt: "+str(pnginfo)}]
            }

        r = requests.post(
        "https://api.paste.ee/v1/pastes", data=str(data).replace('\'','"'), headers=pe_headers)
        details_link = r.json()['link']

        return details_link