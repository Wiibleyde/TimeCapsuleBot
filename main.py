import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ext.commands import has_permissions, MissingPermissions
import datetime

from prgrmUtils.config import ConfigService
from services.CapsuleManager import CapsuleManagerService, CapsuleObject
from botUtils.BotLogs import BotLoggerService

# ==================================================================
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())
# ==================================================================

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f"Starting..."))
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
    botLogger.addLog(interaction.user.id,"ajouter",f"date:{date} message:{message}")
    try:
        date = capsuleManager.readDate(date)
        if date < datetime.datetime.now():
            await interaction.response.send_message("La date ne peux pas être dans le passé", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("La date n'est pas au bon format (dd/mm/YYYY HHhMM)", ephemeral=True)
        return
    capsuleManager.addCapsule(interaction.user.id,date,message)
    await interaction.response.send_message(f"Votre capsule a bien été enregistrée pour le {date.strftime('%d/%m/%Y à %H:%M')}",ephermal=True)

@bot.tree.command(name="voir", description="Permet de voir les capsules que vous avez enregistrées")
async def voir(interaction: discord.Interaction):
    botLogger.addLog(interaction.user.id,"voir")
    capsules = capsuleManager.getCapsuleByUserDiscordId(interaction.user.id)
    if len(capsules) == 0:
        await interaction.response.send_message("Vous n'avez pas de capsules enregistrées", ephemeral=True)
        return
    embed = discord.Embed(title="Vos capsules",color=0x457FEB)
    for counter in range(24,0,-1):
        try:
            embed.add_field(name=f"Capsule n°{counter}",value=f"ID : {capsules[counter-1][0]}\nDate prévue : {capsules[counter-1][3]}\nMessage : {capsules[counter-1][4]}\n Envoyée : {'Oui' if capsules[counter-1][4]==1 else 'Non'}",inline=False)
        except IndexError:
            pass
    await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="supprimer", description="Permet de supprimer une capsule")
async def supprimer(interaction: discord.Interaction, capsuleid:int):
    botLogger.addLog(interaction.user.id,"supprimer",f"capsuleid:{capsuleid}")
    capsule = capsuleManager.getCapsuleById(capsuleid)
    if capsule is None:
        await interaction.response.send_message("Cette capsule n'existe pas", ephemeral=True)
        return
    if capsule.userDiscordId != interaction.user.id:
        await interaction.response.send_message("Vous ne pouvez pas supprimer une capsule qui ne vous appartient pas", ephemeral=True)
        return
    capsuleManager.deleteCapsuleById(capsuleid)
    await interaction.response.send_message("La capsule a bien été supprimée", ephemeral=True)

@bot.tree.command(name="modifier", description="Permet de modifier une capsule")
async def modifier(interaction: discord.Interaction, capsuleid:int, date:str, message:str):
    botLogger.addLog(interaction.user.id,"modifier",f"capsuleId:{capsuleid} date:{date} message:{message}")
    try:
        date = capsuleManager.readDate(date)
        if date < datetime.datetime.now():
            await interaction.response.send_message("La date ne peux pas être dans le passé", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("La date n'est pas au bon format (dd/mm/YYYY HHhMM)", ephemeral=True)
        return
    capsule = capsuleManager.getCapsuleById(capsuleid)
    if capsule is None:
        await interaction.response.send_message("Cette capsule n'existe pas", ephemeral=True)
        return
    if capsule.userDiscordId != interaction.user.id:
        await interaction.response.send_message("Vous ne pouvez pas modifier une capsule qui ne vous appartient pas", ephemeral=True)
        return
    capsuleManager.updateCapsuleById(capsuleid,date,message)
    await interaction.response.send_message("La capsule a bien été modifiée", ephemeral=True)

@bot.tree.command(name="voirall", description="[ADMIN] Permet de voir toutes les capsules")
async def voirall(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    botLogger.addLog(interaction.user.id,"voirall")
    capsules = capsuleManager.getCapsules()
    if len(capsules) == 0:
        await interaction.response.send_message("Il n'y a pas de capsules enregistrées", ephemeral=True)
        return
    embed = discord.Embed(title="Toutes les capsules",color=0x457FEB)
    for counter in range(24,0,-1):
        try:
            embed.add_field(name=f"Capsule n°{counter}",value=f"ID : {capsules[counter-1][0]}\nDate prévue : {capsules[counter-1][3]}\nMessage : {capsules[counter-1][4]}\n Envoyée : {'Oui' if capsules[counter-1][4]==1 else 'Non'}",inline=False)
        except IndexError:
            pass
    await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="supprimerall", description="[ADMIN] Permet de supprimer une capsule")
async def supprimerall(interaction: discord.Interaction, capsuleid:int):
    botLogger.addLog(interaction.user.id,"supprimerall",f"capsuleid:{capsuleid}")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    capsule = capsuleManager.getCapsuleById(capsuleid)
    if capsule is None:
        await interaction.response.send_message("Cette capsule n'existe pas", ephemeral=True)
        return
    capsuleManager.deleteCapsuleById(capsuleid)
    await interaction.response.send_message("La capsule a bien été supprimée", ephemeral=True)

@bot.tree.command(name="modifierall", description="[ADMIN] Permet de modifier une capsule")
async def modifierall(interaction: discord.Interaction, capsuleid:int, date:str, message:str):
    botLogger.addLog(interaction.user.id,"modifierall",f"capsuleid:{capsuleid} date:{date} message:{message}")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    try:
        date = capsuleManager.readDate(date)
        if date < datetime.datetime.now():
            await interaction.response.send_message("La date ne peux pas être dans le passé", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("La date n'est pas au bon format (dd/mm/YYYY HHhMM)", ephemeral=True)
        return
    capsule = capsuleManager.getCapsuleById(capsuleid)
    if capsule is None:
        await interaction.response.send_message("Cette capsule n'existe pas", ephemeral=True)
        return
    capsuleManager.updateCapsuleById(capsuleid,date,message)
    await interaction.response.send_message("La capsule a bien été modifiée", ephemeral=True)

@bot.tree.command(name="forcerenvoi", description="[ADMIN] Permet de forcer l'envoi d'une capsule")
async def forcerenvoi(interaction: discord.Interaction, capsuleid:int):
    botLogger.addLog(interaction.user.id,"forcerenvoi",f"capsuleid:{capsuleid}")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    capsule = capsuleManager.getCapsuleById(capsuleid)
    if capsule is None:
        await interaction.response.send_message("Cette capsule n'existe pas", ephemeral=True)
        return
    if capsule.sent == 1:
        await interaction.response.send_message("Cette capsule a déjà été envoyée", ephemeral=True)
        return
    capsuleManager.forceSendCapsuleById(capsuleid)
    await interaction.response.send_message("La capsule a bien été envoyée", ephemeral=True)

@bot.tree.command(name="forcerenvoiall", description="[ADMIN] Permet de forcer l'envoi d'une capsule")
async def forcerenvoiall(interaction: discord.Interaction, capsuleid:int):
    botLogger.addLog(interaction.user.id,"forcerenvoiall",f"capsuleid:{capsuleid}")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    capsule = capsuleManager.getCapsuleById(capsuleid)
    if capsule is None:
        await interaction.response.send_message("Cette capsule n'existe pas", ephemeral=True)
        return
    if capsule.sent == 1:
        await interaction.response.send_message("Cette capsule a déjà été envoyée", ephemeral=True)
        return
    capsuleManager.forceSendCapsuleById(capsuleid)
    await interaction.response.send_message("La capsule a bien été envoyée", ephemeral=True)

@bot.tree.command(name="setcapsulechannel", description="[ADMIN] Définir le salon ou seront envoyés les capsules")
async def setcapsulechannel(interaction: discord.Interaction, channel:discord.TextChannel):
    botLogger.addLog(interaction.user.id,"setcapsulechannel",f"channel:{channel.id}")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    config.setCapsuleChannel(channel.id)
    await interaction.response.send_message(f"Le salon des capsules a été défini sur {channel.mention}", ephemeral=True)

@bot.tree.command(name="forcereload",description="[ADMIN] Forcer un reload de la loop (check des capsules)")
async def forcereload(interaction: discord.Interaction):
    botLogger.addLog(interaction.user.id,"forcereload")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    checkForCapsules.restart()
    await interaction.response.send_message("Reload effectué", ephemeral=True)

@bot.tree.command(name="logs",description="[ADMIN] Afficher les logs")
async def logs(interaction: discord.Interaction):
    botLogger.addLog(interaction.user.id,"logs")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    logs = botLogger.get25LastLogs()
    embed = discord.Embed(title="Logs", color=0x457FEB)
    for log in logs:
        embed.add_field(name=f"{log[0]} - {log[1]}",value=f"{log[2]}\nCommande : {log[3]}\nArguments : {log[4]}",inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="userlogs",description="[ADMIN] Afficher les logs d'un utilisateur")
async def userlogs(interaction: discord.Interaction, user:discord.User):
    botLogger.addLog(interaction.user.id,"userlogs",f"user:{user.id}")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande", ephemeral=True)
        return
    logs = botLogger.get25LastLogsByUser(user.id)
    embed = discord.Embed(title="Logs", color=0x457FEB)
    for log in logs:
        embed.add_field(name=f"{log[0]} - {log[1]}",value=f"{log[2]}\nCommande : {log[3]}\nArguments : {log[4]}",inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tasks.loop(hours=1)
async def checkForCapsules():
    print("Checking for capsules")
    capsules = capsuleManager.getCapsules()
    goodCapsules = []
    current_time = datetime.datetime.now()
    one_hour_ago = current_time - datetime.timedelta(hours=1)
    for capsule in capsules:
        capsule_time = datetime.datetime.strptime(capsule[3], "%Y-%m-%d %H:%M:%S")
        if capsule_time > one_hour_ago and capsule_time <= current_time:
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
    capsules = capsuleManager.getCapsuleCountNotSent()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f"{capsules} capsules"))
        
if __name__=='__main__':
    config = ConfigService("config.yml")
    botToken = config.getBotToken()
    capsuleManager = CapsuleManagerService("database.db")
    botLogger = BotLoggerService("bot.log.db")
    bot.run(botToken)