# Discord bot, should achieve the following:
# Create voice channels, assign roles to users, limit access based on those roles
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import bot_settings

client = discord.Client()
bot = commands.Bot(command_prefix="?server-sent:")

@bot.event
async def on_ready():
    print("Let's get meshing!")
    print("Running on API version", discord.__version__)

@bot.event
async def on_message(message):
    # Required for commands to work
    await bot.process_commands(message)

@bot.command(pass_context=True)
async def create_channel(ctx, *args):
    '''
    Creates a new incremented channel, then assigns 
    join permissions to everyone that should be in the session
    (which are given as args) on a per user basis.
    '''
    # Get details from params
    guild = ctx.message.guild
    channel_name = args[0]
    
    # Get the default role, override it so nobody has join permissions
    role_default = guild.default_role

    # Decide on the category to place it under
    category = discord.utils.get(guild.categories, name="Meshwell")
    # Create the channel and enable certain users to connect only
    channel = await guild.create_voice_channel(name=channel_name, category=category)
    await channel.set_permissions(role_default, connect=False)

    # Assign members that can access this channel
    if len(args) > 1:
        for index in range(1, len(args)):
            member = guild.get_member_named(args[index])
            if member is not None:
                await channel.set_permissions(member, connect=True)
    
@bot.command(pass_context=True)
async def delete_channel(ctx, channel_name):
    '''
    Deletes the channel name given
    '''
    guild = ctx.message.guild
    channel = discord.utils.get(guild.channels, name=channel_name)
    await channel.delete()

bot.run(bot_settings.key)