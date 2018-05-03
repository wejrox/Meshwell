# Discord bot, should achieve the following:
# Create voice channels, assign roles to users, limit access based on those roles
import discord
import asyncio
from discord.ext import commands
import bot_settings # Private file, as my bot key is private!
import query_data
# Database connection
import MySQLdb
import sys
# Run code on exit of script
import atexit

debug = False
bot = commands.Bot(command_prefix=bot_settings.cmd_prefix)

# Database
db_connection = MySQLdb.connect(host=bot_settings.host, 
								user=bot_settings.user, 
								passwd=bot_settings.password, 
								db=bot_settings.database_name
								)

async def auto_manage_channels():
	'''
	Gets all upcoming sessions that have a start and end time
	and the discord names of those players in the sessions.
	Creates a channel for them.
	Gets all sessions that are over x amount of time old.
	Deletes the channel that is for that session.
	Sends DM to discord user, telling them to rate the session
	'''
	await bot.wait_until_ready()
	# Get guild identity
	print("=================\nSetup\n=================")
	print("Getting guild...")
	# Gets meshwell server by guild id
	guild = bot.get_guild(bot_settings.guild_id)
	if guild is not None:
		print("Guild name: ", guild)
	else:
		print("Guild not found, bot cannot function! \nExiting...")
		sys.exit()
	# Get the meshwell category by channel id
	print("Getting category...")
	category = guild.get_channel(bot_settings.category_id)
	if category is not None:
		print("Category name: ", category)
	else:
		print("Category not found, bot cannot function! \nExiting...")
		sys.exit()
	# Query database every x timeframe
	print("=================\nRunning\n=================")
	while not bot.is_closed():
		# Get upcoming sessions
		cursor = db_connection.cursor()
		cursor.execute(query_data.upcoming_sessions_query)
		upcoming = cursor.fetchall()
		# Create channels if needed
		if len(upcoming) > 0:
			# Run only if in debug mode for performance reasons
			if debug:
				print("Fetched upcoming session details [session_id, discord_id]:")
				for row in upcoming:
					print (row[0], row[1])
			print("Creating channels...")
			for row in upcoming:
				if row[1] is not None:
					# Get channel if exists (CONSIDER CHANGING TO guild.voice_channel)
					channel = discord.utils.get(guild.channels, name=str(row[0]))
					# Create channel if it doesn't exist
					if channel is None:
						channel = await guild.create_voice_channel(name=str(row[0]), category=category, reason="Automated channel creation on session start")
						print("New channel created")
					else:
						print("Channel exists, adding users")
					# Set default perms
					await channel.set_permissions(guild.default_role, connect=False)
					# Assign permissions to channel for users
					member = guild.get_member_named(row[1])
					if member is not None:
						await channel.set_permissions(member, connect=True)
						print("Permissions set")
						# Send invite to the players discord
						invite = await channel.create_invite(reason="Automated invite creation")
						print("Invite created: " + str(invite))
						message = "Hi! This message is to let you know that your session now has a voice channel available!\n" + str(invite)
						print(message)
						await member.send(content=message)
					else:
						print("Guild does not have member '"+row[1]+"', they may not be in the server!")
		else:
			print("No upcoming sessions")
		cursor.close()

		# Get past sessions to be removed
		cursor = db_connection.cursor()
		cursor.execute(query_data.past_sessions_query)
		past = cursor.fetchall()
		# Delete channels if needed
		if len(past) > 0:
			# Run only if in debug mode for performance reasons
			if debug:
				print("Sessions to end [session_id, discord_id]")
				for row in past:
					print (row[0], row[1])
			print("Handling session end...")
			for row in past:
				if row[0] is not None and row[1] is not None:
					# Get channel
					member = guild.get_member_named(str(row[1]))
					channel = discord.utils.get(guild.channels, name=str(row[0]))
					rate_url = "https://www.meshwell.com/dashboard/session/rate/"+str(row[2])
					# Send message to members to rate session
					message = "We hope you've enjoyed your session! \nPlease follow the link to rate your session in order to receive the best matching experience.\n"+str(rate_url)
					await member.send(content=message)
					# If channel exists, delete it
					if channel is not None:
						await channel.delete(reason="Automated channel delete on session end")
		else:
			print("No sessions to delete")
					
		# Wait x seconds before checking again
		await asyncio.sleep(query_data.query_interval)
		print("=================\nRe-Checking Sessions\n=================")

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
	category = guild.get_channel(bot_settings.category_id)
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

def exit_handler():
	'''
	Code that is run when the program either 
	finishes (impossible) 
	or 
	is terminated with Ctrl+C or other KBD interrupt
	'''
	# Close all open connections
	try:
		auto_manage_channels.cancel()
		print("Cancelled channel creation")
	except:
		pass
	try:
		db_connection.close()
		print("Closed database connection")
	except:
		pass
	try:
		bot.close()
		print("Turned off the bot")
	except:
		pass


# Initiate channel creator
auto_manage_channels = bot.loop.create_task(auto_manage_channels())

# Run code at exit
atexit.register(exit_handler)

# Run bot
bot.run(bot_settings.key)