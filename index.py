import discord
from modules.generation import create, variation, upscale
from modules.pastee import pastee_post
from PIL import ImageStat, Image
import json
import queue
import requests
import threading
from io import BytesIO



from discord.commands import Option
intents = discord.Intents.default()

intents.message_content = True
intents.guild_reactions = True
intents.reactions = True

client = discord.Bot(intents=intents)


q = queue.Queue()


url = "http://127.0.0.1:7860"
file_name = 'image_settings.json'
g_ids =[1010879727407472670]

with open('settings.json') as settings:
    data = json.load(settings)
    token = data["TOKEN"]

async def get_button_interaction(interaction, ctx, sent_message):

    if type(sent_message) == discord.interactions.InteractionMessage:

        original_message = await interaction.response.send_message('thinking... <a:loading:1047116523757654047>')
        get_attachment_message = await ctx.channel.fetch_message(sent_message.id)

        return original_message, get_attachment_message

    elif type(sent_message) == discord.interactions.Interaction:

        original_message = await interaction.response.send_message('thinking... <a:loading:1047116523757654047>')
        get_attachment_interaction = await sent_message.original_response()
        get_attachment_message = await ctx.channel.fetch_message(get_attachment_interaction.id)

        return original_message, get_attachment_message


def rgb2int(rgb): return (rgb[0]<<16)+(rgb[1]<<8)+rgb[2]


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # if message.content == 'balls':
    #     response3 = requests.get(url=f'{url}/sdapi/v1/sd-models')
    #     print(response3.json())
 

@client.slash_command(guild_ids=[g_ids[0]], description="makes your words reality")
async def think(ctx, prompt: Option(str, description="What you WANT in your image", required=True),
neg_prompt: Option(str, description="What you DON'T WANT in your image (Not Required)", required=False)): 

    sent_message = []

    # Buttons code

    class MyView(discord.ui.View):
        @discord.ui.button(label="Make Variation", style=discord.ButtonStyle.secondary, emoji="🎨") 
        async def second_button_callback(self, button, interaction):

            variation_payload, get_attachment_message = await get_button_interaction(interaction, ctx, sent_message[0])
            arr, image, pnginfo = await variation(prompt, get_attachment_message.embeds[0].image.url)
            details_link = await pastee_post(prompt, pnginfo)
            embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'[Variation of: ](https://discord.com/channels/{get_attachment_message.guild.id}/{get_attachment_message.channel.id}/{get_attachment_message.id})**{prompt}**\n[(Generation Settings)]({details_link})')
            embed.set_image(url="attachment://test.png")
            sent_message_body = await variation_payload.edit_original_response(file=discord.File(fp=arr, filename='test.png'), embed=embed, content='', view=MyView())
            sent_message.insert(0, sent_message_body)

        @discord.ui.button(label="Quick Upscale", style=discord.ButtonStyle.secondary, emoji="💨") 
        async def first_button_callback(self, button, interaction):

            original_message, get_attachment_message = await get_button_interaction(interaction, ctx, sent_message[0])

            check_image_size = requests.get(get_attachment_message.embeds[0].image.url)
            check_image_size = Image.open(BytesIO(check_image_size.content))
            width, height = check_image_size.size

            if width >= 2048 or height >= 2048:
                 await original_message.edit_original_response(content='Image too large to upscale')
            else:
                arr, image = await upscale(get_attachment_message.embeds[0].image.url)
                details_link = await pastee_post(prompt, 'test')
                embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'[Upscaled: ](https://discord.com/channels/{get_attachment_message.guild.id}/{get_attachment_message.channel.id}/{get_attachment_message.id})**{prompt}**\n[(Generation Settings)]({details_link})')
                embed.set_image(url="attachment://test.png")
                sent_message_body = await original_message.edit_original_response(file=discord.File(fp=arr, filename='test.png'), embed=embed, content='', view=MyView())
                sent_message.insert(0, sent_message_body)

        @discord.ui.button(label="Detailed Upscale", style=discord.ButtonStyle.secondary, emoji="🔍") 
        async def third_button_callback(self, button, interaction):

            original_message, get_attachment_message = await get_button_interaction(interaction, ctx, sent_message[0])
            arr, image = await upscale(get_attachment_message.embeds[0].image.url)
            details_link = await pastee_post(prompt, 'test')
            embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'[Upscaled: ](https://discord.com/channels/{get_attachment_message.guild.id}/{get_attachment_message.channel.id}/{get_attachment_message.id})**{prompt}**\n[(Generation Settings)]({details_link})')
            embed.set_image(url="attachment://test.png")
            sent_message_body = await original_message.edit_original_response(file=discord.File(fp=arr, filename='test.png'), embed=embed, content='', view=MyView())
            sent_message.insert(0, sent_message_body)

    # Original payload code

    
    sent_message_body = await ctx.response.send_message('thinking... <a:loading:1047116523757654047>')
    sent_message.insert(0, sent_message_body)
    arr, image, pnginfo = await create(prompt, neg_prompt)
    details_link = await pastee_post(prompt, pnginfo)
    embed = discord.Embed(color=rgb2int(tuple(ImageStat.Stat(image).median)),description=f'**{prompt}**\n[(Generation Settings)]({details_link})')
    embed.set_image(url="attachment://test.png")
    await sent_message[0].edit_original_response(file=discord.File(fp=arr, filename='test.png'), embed=embed, content='', view=MyView())





























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