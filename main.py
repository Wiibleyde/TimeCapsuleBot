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
    except ValueError:
        await interaction.response.send_message("La date n'est pas au bon format (dd/mm/YYYY HHhMM)")
        return
    capsuleManager.addCapsule(interaction.user.id,date,message)
    await interaction.response.send_message(f"Votre capsule a bien été enregistrée pour le {date.strftime('%d/%m/%Y à %H:%M')}")

@tasks.loop(hours=1)
async def checkForCapsules():
    print("Checking for capsules")
    capsules = capsuleManager.getCapsules()
    goodCapsules = []
    for capsule in capsules:
        if datetime.datetime.strptime(capsule[3],"%Y-%m-%d %H:%M:%S") > datetime.datetime.now() - datetime.timedelta(hours=1):
            goodCapsules.append(CapsuleObject(*capsule))
    for capsule in goodCapsules:
        channel = int(config.getCapsuleChannel())
        channel = bot.get_channel(channel)
        user = bot.get_user(capsule.userDiscordId)
        embed = discord.Embed(title="Nouvelle capsule !", color=0x457FEB)
        embed.add_field(name="Date d'écriture",value=capsule.writingDate,inline=False)
        embed.add_field(name="Contenu de la capsule", value=capsule.message)
        embed.set_footer(text=f"Par : {user}")
        await channel.send(embed=embed)
        
if __name__=='__main__':
    config = ConfigService("config.yml")
    botToken = config.getBotToken()
    capsuleManager = CapsuleManagerService("database.db")
    bot.run(botToken)