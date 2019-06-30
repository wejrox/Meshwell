#
# A discord bot which provides functionality for the following tasks:
# Dynamic voice channel creation, user role assignment, room access limitation based on roles.
#
import discord
import asyncio
from discord.ext import commands
import bot_settings # Private file used for private key access.
import query_data

# Database connection.
import MySQLdb
import sys

# Run code on exit of script.
import atexit

debug = True
bot = commands.Bot(command_prefix=bot_settings.cmd_prefix)
us_session_id = 0
us_discord_id = 1
ps_session_id = 0
ps_discord_id = 1
ps_session_profile_id = 2

# Open database connection.
db_connection = MySQLdb.connect(host=bot_settings.host,
								user=bot_settings.user,
								passwd=bot_settings.password,
								db=bot_settings.database_name)


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

	# Get guild/server identity,
	print("=================\nSetup\n=================")
	print("Finding guild (server)...")

	# Gets meshwell server by guild (server) id.
	guild = bot.get_guild(bot_settings.guild_id)
	if guild is not None:
		print("Guild name: ", guild)
	else:
		print("Guild not found, bot cannot function! \nExiting...")
		sys.exit()

	# Get the meshwell category by channel id.
	print("Getting channel...")
	category = guild.get_channel(bot_settings.category_id)
	if category is not None:
		print("Category name: ", category)
	else:
		print("Category not found, bot cannot function! \nExiting...")
		sys.exit()

	# Query database every x timeframe.
	print("=================\nRunning\n=================")
	while not bot.is_closed():
		print("Checking for sessions")

		# Get upcoming sessions.
		cursor = db_connection.cursor()
		if debug: print("Made cursor.")

		cursor.execute(query_data.upcoming_sessions_query)
		if debug: print("Executed upcoming sessions query.")

		upcoming = cursor.fetchall()
		if debug: print("Retrieved query results.")

		# Create channels if needed.
		if len(upcoming) > 0:
			if debug: print("Upcoming sessions exist.")

			# Run only if in debug mode for performance reasons.
			if debug:
				print("Fetched upcoming session details [session_id, discord_id]:")
				for row in upcoming:
					print (row[us_session_id], row[us_discord_id])

			if debug: print("Creating channels...")
			for row in upcoming:
				if row[us_discord_id] is not None:

					# Get channel if exists (CONSIDER CHANGING TO guild.voice_channel).
					channel = discord.utils.get(guild.channels, name=str(row[us_session_id]))

					# Create voice channel for the session if it doesn't exist.
					if channel is None:
						channel = await guild.create_voice_channel(name=str(row[us_session_id]), category=category, reason="Automated channel creation on session start")
						if debug: print("New channel created")
					else:
						if debug: print("Channel already exists")

					# Set default channel permissions.
					await channel.set_permissions(guild.default_role, connect=False)

					# Assign access permissions to channel for users in the related session.
					member = guild.get_member(int(row[us_discord_id]))

					# Only attempt to add permissions if the user has linked their account.
					if member is not None:
						await channel.set_permissions(member, connect=True)
						if debug: print("Permissions set")

						# Send invite to the players discord.
						invite = await channel.create_invite(reason="Automated invite creation")
						if debug: print("Invite created: " + str(invite))
						message = "Hi! This automated message is to let you know that your session now has a voice channel available!\n" + str(invite)
						if debug: print(message)
						await member.send(content=message)
					else:
						print("Guild does not have member \'"+row[us_discord_id]+"\', they may not be in the server!")
		else:
			print("No upcoming sessions")
		cursor.close()

		# Get past sessions to be removed.
		cursor = db_connection.cursor()
		cursor.execute(query_data.past_sessions_query)
		past = cursor.fetchall()

		# Delete channels if needed.
		if len(past) > 0:

			# Run only if in debug mode for performance reasons.
			if debug:
				print("Sessions to end [session_id, discord_id]")
				for row in past:
					print (row[ps_session_id], row[ps_discord_id])

			print("Handling session end...")
			for row in past:
				if row[ps_session_id] is not None and row[ps_discord_id] is not None:

					# Get channel.
					member = guild.get_member(int(row[ps_discord_id]))
					channel = discord.utils.get(guild.channels, name=str(row[ps_session_id]))
					rate_url = "https://www.meshwell.com/dashboard/"

					# Send message to members to rate session.
					message = "We hope you've enjoyed your session! \nPlease visit the dashboard and rate your session in order to receive the best matching experience and improved recommendations.\n"+str(rate_url)
					await member.send(content=message)

					# If channel exists, delete it.
					if channel is not None:
						await channel.delete(reason="Automated channel delete on session end")
		else:
			print("No sessions to delete")

		# Wait x seconds before checking again.
		await asyncio.sleep(query_data.query_interval)
		print("=================\nRe-Checking Sessions\n=================")


@bot.event
async def on_ready():
	print("Let's get meshing!")
	print("Running on API version ", discord.__version__)


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
	# Get details from params.
	guild = ctx.message.guild
	channel_name = args[0]

	# Get the default role, override it so nobody has join permissions.
	role_default = guild.default_role
	category = guild.get_channel(bot_settings.category_id)

	# Create the channel and enable certain users to connect only.
	channel = await guild.create_voice_channel(name=channel_name, category=category)
	await channel.set_permissions(role_default, connect=False)

	# Assign members that can access this channel.
	if len(args) > 1:

		# Assign each of the users provided, starting at 1 since arg 0 is the channel name.
		for index in range(1, len(args)):
			member = guild.get_member_named(args[index])

			# Only attempt to provide permissions if the user has connected their discord account.
			if member is not None:
				await channel.set_permissions(member, connect=True)

				# Send invite link to the player via discord.
				invite = await channel.create_invite(reason="Automated invite creation")
				message = "Hi! This message is to let you know that your session now has a voice channel available!\n" + str(invite)
				await member.send(content=message)


def exit_handler():
	'''
	Code that is run when the program either 
	finishes (only closes if an exception occurs) 
	or 
	is terminated with Ctrl+C or other KBD interrupt
	'''
	# Close all open connections.
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


# Initiate channel creator infinite loop.
auto_manage_channels = bot.loop.create_task(auto_manage_channels())

# Run code at exit.
atexit.register(exit_handler)

# Run bot.
bot.run(bot_settings.key)
