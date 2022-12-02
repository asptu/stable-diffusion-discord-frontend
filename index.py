import discord
from commands.generation import create, variation
from PIL import ImageStat
import json
import requests

from discord.commands import Option
intents = discord.Intents.default()

intents.message_content = True
intents.guild_reactions = True
intents.reactions = True

client = discord.Bot(intents=intents)

url = "http://127.0.0.1:7860"
file_name = 'image_settings.json'
g_ids =[1010879727407472670]

with open('settings.json') as settings:
    data = json.load(settings)
    token = data["TOKEN"]
    pb_token = data['PB_TOKEN']
    pb_pass = data['PB_PASSWORD']
    pb_user = data['PB_USERNAME']

login = requests.post("https://pastebin.com/api/api_login.php", data={
    'api_dev_key': pb_token,
    'api_user_name': pb_user,
    'api_user_password': pb_pass
})
print("Login status: ", login.status_code if login.status_code != 200 else "OK/200")
print("User token: ", login.text)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
                    
    if message.content.startswith('-think'):

        if message.reference is not None:

            reference_image = await message.channel.fetch_message(message.reference.message_id)

            if reference_image.embeds:
                print('found embed')
                print(reference_image.embeds[0].url)
                prompt = message.content[7:]

                img_url = reference_image.embeds[0].url
                sent_message = await message.channel.send('thinking...')

                arr, image, json_obj = variation(prompt,img_url)
                image3 = discord.File(fp=arr, filename='test.png')

                json_final = {
                        f"{sent_message.id}": {
                            "steps": int(json_obj['steps']),
                            "sampler_name": str(json_obj['sampler_name']),
                            "seed": int(json_obj['seed']),
                            "cfg_scale": float(json_obj['cfg_scale']),
                            "width": int(json_obj['width']),
                            "height": int(json_obj['height']),
                            "model": str(json_obj['model']),
                            "denoising_strength": float(json_obj['denoising_strength'])
                        }
                }

                with open(file_name, 'r') as f:
                    data = json.load(f)
                    data['images'].append(json_final)
                with open(file_name, 'w') as f:
                    f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
                
                def rgb2int(rgb): return (rgb[0]<<16)+(rgb[1]<<8)+rgb[2]
                embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'[Variation of: ](https://discord.com/channels/{get_attachment_message.guild.id}/{get_attachment_message.channel.id}/{get_attachment_message.id})**{prompt}**')
                embed.set_image(url="attachment://test.png")
                await sent_message.edit(file=image3, embed=embed, content='', view=MyView())

                await sent_message.edit(content='',file=discord.File("output.png", filename="output.png"))

            elif reference_image.attachments:                    
                print('found attachment')
                print(reference_image.attachments[0].url)

                prompt = message.content[7:]

                img_url = reference_image.attachments[0].url
                sent_message = await message.channel.send('thinking...')

                await create(prompt,img_url,url)
                await sent_message.edit(content='',file=discord.File("output.png", filename="output.png"))
        
        else:

            prompt = message.content[7:]
            sent_message = await message.channel.send('thinking... <a:loading:1047116523757654047>')

            arr, image, info = await create(prompt)

            image3 = discord.File(fp=arr, filename='test.png')
            class MyView(discord.ui.View):
                @discord.ui.button(label="Make Variation", style=discord.ButtonStyle.secondary, emoji="🎨") 
                async def second_button_callback(self, button, interaction):

                    original_message = await interaction.response.send_message('thinking... <a:loading:1047116523757654047>')
                    get_attachment = await message.channel.fetch_message(sent_message.id)
                    arr, image, info = await variation(prompt, get_attachment.embeds[0].image.url)

                    image3 = discord.File(fp=arr, filename='test.png')
                    def rgb2int(rgb): return (rgb[0]<<16)+(rgb[1]<<8)+rgb[2]
                    embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'Varitation of: **{prompt}**')
                    embed.set_image(url="attachment://test.png")
                    await original_message.edit_original_response(file=image3, embed=embed, content='', view=MyView())


                @discord.ui.button(label="Reveal Settings", style=discord.ButtonStyle.secondary, emoji="🔨") 

                async def first_button_callback(self, button, interaction):
                    await interaction.response.send_message(info)

            def rgb2int(rgb): return (rgb[0]<<16)+(rgb[1]<<8)+rgb[2]
            embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'**{prompt}**')
            embed.set_image(url="attachment://test.png")
            await sent_message.edit(file=image3, embed=embed, content='', view=MyView())




@client.slash_command(guild_ids=[g_ids[0]], description="makes your words reality")
async def think(ctx, prompt: Option(str, description="get a bit crazy wit it")): 

    sent_message = await ctx.response.send_message('thinking... <a:loading:1047116523757654047>')
    arr, image, info = await create(prompt)
    image3 = discord.File(fp=arr, filename='test.png')
    class MyView(discord.ui.View):
        @discord.ui.button(label="Make Variation", style=discord.ButtonStyle.secondary, emoji="🎨") 
        async def second_button_callback(self, button, interaction):

            variation_payload = await interaction.response.send_message('thinking... <a:loading:1047116523757654047>')
            get_attachment_interaction = await sent_message.original_response()
            get_attachment_message = await ctx.channel.fetch_message(get_attachment_interaction.id)

            arr, image, info = await variation(prompt, get_attachment_message.embeds[0].image.url)
            image3 = discord.File(fp=arr, filename='test.png')

            data = {
                'api_option': 'paste',
                'api_dev_key':pb_token,
                'api_paste_code':info,
                'api_paste_name':prompt[:97] + (prompt[97:] and '...'),
                'api_user_key': login.text
                }

            r = requests.post("https://pastebin.com/api/api_post.php", data=data)
            
            def rgb2int(rgb): return (rgb[0]<<16)+(rgb[1]<<8)+rgb[2]
            embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'[Variation of: ](https://discord.com/channels/{get_attachment_message.guild.id}/{get_attachment_message.channel.id}/{get_attachment_message.id})**{prompt}**\n[(Generation Settings)]({r.text})')
            embed.set_image(url="attachment://test.png")
            await variation_payload.edit_original_response(file=image3, embed=embed, content='', view=MyView())


    data = {
        'api_option': 'paste',
        'api_dev_key':pb_token,
        'api_paste_code':info,
        'api_paste_name':prompt[:97] + (prompt[97:] and '...'),
        'api_user_key': login.text
        }

    r = requests.post("https://pastebin.com/api/api_post.php", data=data)
    def rgb2int(rgb): return (rgb[0]<<16)+(rgb[1]<<8)+rgb[2]
    embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'**{prompt}**\n[(Generation Settings)]({r.text})')
    embed.set_image(url="attachment://test.png")
    await sent_message.edit_original_response(file=image3, embed=embed, content='', view=MyView())



@client.slash_command(guild_ids=[g_ids[0]], description="dial in those numbers")
async def thinkadv(ctx, 
prompt: Option(str, description="The text input", required=True),
negative_prompt: Option(str, description='Negative prompt (Default = '')', required=False, default=''),
int_image: Option(str, description='Image url of base image (Default = '')', required=False, default=''),
steps: Option(int, description="Amount of step iterations (Default = 20)", required=True ,default=20, min_value=1, max_value=50),
seed: Option(int, description="Procedurally generated noise seed (Default = -1)", required=True, default=-1),
cfg: Option(float, description="Stylisation scale (Default = 7)", required=True, default=7.0, min_value=1, max_value=30),
width: Option(int, description="Width of image (Default = 768)", choices=[512,576,640,704,768,832,896,960,1024], required=True, default=768),
height: Option(int, description="Height of image (Default = 768)", choices=[512,576,640,704,768,832,896,960,1024], required=True, default=768),
model: Option(str, description="Custom generation model (Default = SD2)", choices=['elden ring','SD2','studio ghibli','spider-verse'], required=True, default='SD2'),
sampler_name: Option(str, description="Name of diffusion sampler (Default = Euler A", choices=['Euler a','Euler','LMS','Heun','DPM2','DPM2 a','DPM++ 2S a','DPM++ 2M','DPM++ SDE','DPM fast','DPM adaptive','LMS Karras','DPM2 Karras','DPM2 a Karras','DPM2 a Karras','DPM++ 2M Karras','DPM++ SDE Karras','DDIM','PLMS'], required=True, default='Euler a'),
denoising_strength: Option(float, description="Amount image is diffused", required=True, default=0.7)
): 



    print(prompt)
    print(negative_prompt)
    print(int_image)
    print(steps)
    print(seed)
    print(cfg)
    print(width)
    print(height)
    print(model)
    print(sampler_name)
    print(denoising_strength)



client.run(token)