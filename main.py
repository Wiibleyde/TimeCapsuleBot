import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ext.commands import has_permissions, MissingPermissions
import datetime

from prgrmUtils.config import ConfigService
from services.CapsuleManager import CapsuleManagerService, CapsuleObject

# ==================================================================
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())
# ==================================================================

@bot.event
async def on_ready():
    print("Bot is ready")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
        print(f"Commands: {synced}")
    except Exception as e:
        print(e)
    checkForCapsules.start()
    checkForCapsuleCount.start()

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        await ctx.send("Command not found")
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("Missing required argument")
    elif isinstance(error,commands.MissingPermissions):
        await ctx.send("You don't have the permissions to use this command")
    else:
        await ctx.send("An error occured")

@bot.tree.command(name="ajouter", description="Permet l'ajout d'une capsule qui sera révélée à la date. (Format de la date : 'dd/mm/YYYY HHhMM)")
async def ajouter(interaction: discord.Interaction, date:str, message:str):
    try:
        date = capsuleManager.readDate(date)
        if date < datetime.datetime.now():
            await interaction.response.send_message("La date ne peux pas être dans le passé", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("La date n'est pas au bon format (dd/mm/YYYY HHhMM)", ephemeral=True)
        return
    capsuleManager.addCapsule(interaction.user.id,date,message)
    await interaction.response.send_message(f"Votre capsule a bien été enregistrée pour le {date.strftime('%d/%m/%Y à %H:%M')}")

@bot.tree.command(name="voir", description="Permet de voir les capsules que vous avez enregistrées")
async def voir(interaction: discord.Interaction):
    capsules = capsuleManager.getCapsuleByUserDiscordId(interaction.user.id)
    if len(capsules) == 0:
        await interaction.response.send_message("Vous n'avez pas de capsules enregistrées", ephemeral=True)
        return
    embed = discord.Embed(title="Vos capsules",color=0x457FEB)
    for counter in range(24,0,-1):
        try:
            embed.add_field(name=f"Capsule n°{counter}",value=f"Date prévue : {capsules[counter-1][3]}\nMessage : {capsules[counter-1][4]}\n Envoyée : {'Oui' if capsules[counter-1][4] else 'Non'}",inline=False)
        except IndexError:
            pass
    await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="setcapsulechannel", description="[ADMIN] Définir le salon ou seront envoyés les capsules")
@has_permissions(administrator=True)
async def setcapsulechannel(interaction: discord.Interaction, channel:discord.TextChannel):
    config.setCapsuleChannel(channel.id)
    await interaction.response.send_message(f"Le salon des capsules a été défini sur {channel.mention}", ephemeral=True)

@bot.tree.command(name="forcereload",description="[ADMIN] Forcer un reload des capsules")
@has_permissions(administrator=True)
async def forcereload(interaction: discord.Interaction):
    checkForCapsules.restart()
    await interaction.response.send_message("Reload effectué", ephemeral=True)

@tasks.loop(hours=1)
async def checkForCapsules():
    print("Checking for capsules")
    capsules = capsuleManager.getCapsules()
    goodCapsules = []
    for capsule in capsules:
        if datetime.datetime.strptime(capsule[3],"%Y-%m-%d %H:%M:%S") > datetime.datetime.now() - datetime.timedelta(hours=1):
            goodCapsules.append(CapsuleObject(*capsule))
    for capsule in goodCapsules:
        if capsule.sent:
            pass
        else:
            channel = int(config.getCapsuleChannel())
            channel = bot.get_channel(channel)
            user = bot.get_user(capsule.userDiscordId)
            embed = discord.Embed(title="Nouvelle capsule !", color=0x457FEB)
            embed.add_field(name="Date d'écriture",value=capsule.writingDate,inline=False)
            embed.add_field(name="Contenu de la capsule", value=capsule.message)
            embed.set_footer(text=f"Par : {user}")
            await channel.send(embed=embed)
            capsuleManager.setCapsuleSent(capsule.id)

@tasks.loop(seconds=30)
async def checkForCapsuleCount():
    capsules = capsuleManager.getCapsuleCount()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f"{capsules} capsules"))
        
if __name__=='__main__':
    config = ConfigService("config.yml")
    botToken = config.getBotToken()
    capsuleManager = CapsuleManagerService("database.db")
    bot.run(botToken)