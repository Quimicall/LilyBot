import discord
import json
import os
import random
from discord.ext import commands

# Define a variável inventário como um dicionário vazio
inventario = {}

# Define as intents que o bot irá utilizar
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Adiciona as intents ao bot # Cria o bot e define o prefixo dos comandos
bot = commands.Bot(command_prefix=".", case_insensitive=True, intents=intents)


# Define o evento que ocorre quando o bot está pronto
@bot.event
async def on_ready():
    print(f'Conectado como {bot.user.name} - {bot.user.id}')

    # Lê o arquivo de inventário ao iniciar o bot
    with open('inventario.json', 'r') as f:
        global inventario
        inventario = json.load(f)


# Define o evento que ocorre quando o bot entra em um servidor
@bot.event
async def on_guild_join(guild):
    # Cria a pasta do servidor se ela não existir
    folder_path = f"data/{guild.id}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Cria os arquivos do servidor se eles não existirem
    waifus_file = f"{folder_path}/waifus_{guild.id}.json"
    if not os.path.exists(waifus_file):
        with open(waifus_file, "w") as f:
            f.write("{}")

    inventario_file = f"{folder_path}/inventario_{guild.id}.json"
    if not os.path.exists(inventario_file):
        with open(inventario_file, "w") as f:
            f.write("{}")


# Define o comando .waifu
@bot.command()
async def waifu(servidor, nome_waifu):
    with open(f'waifus_{servidor.id}.json', 'w') as f:
        waifus = json.load(f)

    waifu_escolhida = next((w for w in waifus if w["nome"].lower() == nome_waifu.lower()), None)
    if not waifu_escolhida:
        await servidor.send(f"Desculpe, não foi encontrada nenhuma waifu com o nome {nome_waifu}.")
        return

    usuario = str(servidor.author.id)
    inventario_file = f"data/{servidor.id}/inventario_{servidor.id}.json"
    with open(inventario_file, 'r') as f:
        inventario = json.load(f)
    waifus_usuario = inventario.get(usuario, [])
    waifus_usuario.append(waifu_escolhida['nome'])
    inventario[usuario] = waifus_usuario

    with open(inventario_file, 'w') as f:
        json.dump(inventario, f, indent=4)

    await servidor.send(
        f"Parabéns, {servidor.author.mention}! Você adquiriu a waifu {waifu_escolhida['nome']} do anime {waifu_escolhida['anime']}.")


@bot.command()
async def comprar(ctx, canal=None):
    canal = canal or ctx.channel
    await comprarwaifu(ctx.author, canal)


async def comprarwaifu(usuario, ctx):
    with open(f'data/{ctx.guild.id}/waifus_{ctx.guild.id}.json', 'r') as f:
        waifus = json.load(f)

    # Filtra as waifus que ainda não foram adquiridas
    waifus_disponiveis = [w for w in waifus if not w["adquirida"]]

    if not waifus_disponiveis:
        await usuario.send("Todas as waifus já foram adquiridas.")
        return

    waifu_escolhida = random.choice(waifus_disponiveis)
    waifu_escolhida["adquirida"] = True

    with open(f'waifus_{ctx.guild.id}.json', 'w') as f:
        json.dump(waifus, f, indent=4)

    # Adiciona a nova waifu ao inventário do usuário
    with open(f'inventario_{ctx.guild.id}.json', 'r') as f:
        inventario = json.load(f)

    usuario_id = str(usuario.id)
    waifus_usuario = inventario.get(usuario_id, [])
    waifus_usuario.append(waifu_escolhida['nome'])
    inventario[usuario_id] = waifus_usuario

    with open('inventario.json', 'w') as f:
        json.dump(inventario, f, indent=4)

    embed = discord.Embed(title=waifu_escolhida['nome'], description=waifu_escolhida['anime'], color=14626457)
    embed.set_author(name="Nova waifu adquirida!")
    embed.set_image(url=waifu_escolhida['imagem'])
    embed.add_field(name="Level", value="1", inline=True)
    embed.add_field(name="Afinidade", value="0%", inline=True)
    embed.add_field(name="Experiência", value="0/100", inline=False)

    mensagem = f"{usuario.mention}, você adquiriu uma nova waifu!"
    await ctx.send(mensagem, embed=embed)


@bot.command()
async def inventario(ctx, guild, servidor):
    with open(f'data/{ctx.guild.id}/inventario_{ctx.guild.id}.json', 'r') as f:
        inventario = json.load(f)

    usuario = str(ctx.author.id)
    waifus_usuario = inventario.get(usuario, [])

    if not waifus_usuario:
        await ctx.send("Você ainda não adquiriu nenhuma waifu.")
        return

    with open('waifus.json', 'r') as f:
        waifus = json.load(f)

    embed = discord.Embed(title=f"Inventário de {ctx.author.display_name}", color=14626457)

    for waifu_nome in waifus_usuario:
        waifu = next((w for w in waifus if w["nome"] == waifu_nome), None)
        if waifu:
            embed.add_field(
                name=waifu['nome'],
                value=f"Anime: {waifu['anime']}\nLevel: {waifu['level']}\nAfinidade: {waifu['afinidade']}\nExperiência: {waifu['experiencia']}",
                inline=False
            )

    await ctx.send(embed=embed)


@bot.command()
async def adquirir(ctx):
    with open('waifus.json', 'r') as f:
        waifus = json.load(f)

    usuario = str(ctx.author.id)

    with open('inventario.json', 'r') as f:
        inventario = json.load(f)

    waifus_usuario = inventario.get(usuario, [])

    if len(waifus_usuario) >= 10:
        await ctx.send("Você já possui o limite máximo de 10 waifus.")
        return

    waifu_escolhida = random.choice(waifus)

    while waifu_escolhida['nome'] in waifus_usuario:
        waifu_escolhida = random.choice(waifus)

    embed = discord.Embed(title=f"{ctx.author.display_name} adquiriu {waifu_escolhida['nome']}!", color=14626457)
    embed.set_thumbnail(url=waifu_escolhida['imagem'])

    await ctx.send(embed=embed)

    waifus_usuario.append(waifu_escolhida['nome'])
    inventario[usuario] = waifus_usuario

    with open('inventario.json', 'w') as f:
        json.dump(inventario, f, indent=4)


# Rode o bot
bot.run('TOKEN AQUI')
