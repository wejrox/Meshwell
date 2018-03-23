from django.db import models
from django.contrib.auth.models import User

# We are building on top of djangos default user model as it provides authentication already, adding our required fields for meshwell
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.PROTECT)

	USWEST = 'usw'
	USEAST = 'use'
	EUROPE = 'eu'
	OCEANIA = 'oce'
	ASIA = 'as'
	SOUTHAMERICA = 'sam'
	SOUTHAFRICA = 'saf'
	MIDDLEEAST = 'me'

	PREF_SERVER_CHOICES = (
		(USWEST, 'US-West'),
		(USEAST, 'US-East'),
		(EUROPE, 'Europe'),
		(OCEANIA, 'Oceania'),
		(ASIA, 'Asia'),
		(SOUTHAMERICA, 'South America'),
		(SOUTHAFRICA, 'South Africa'),
		(MIDDLEEAST, 'Middle-East'),
	)

	pref_server = models.CharField(
		max_length=3,
		choices=PREF_SERVER_CHOICES,
		default=USWEST,
	)

	birth_date = models.DateField(null=True, blank=False,)
	sessions_played = models.IntegerField(null=False, blank=False, default='0',)
	teamwork_commends = models.IntegerField(null=False, blank=False, default='0',)
	communication_commends = models.IntegerField(null=False, blank=False, default='0',)
	skill_commends = models.IntegerField(null=False, blank=False, default='0',)
	positivity_commends = models.IntegerField(null=False, blank=False, default='0',)

	# The users name on discord, which is limited by them to 32 chars, plus 5 for id. e.g. myname#1205
	discord_name = models.CharField(max_length=37, null=True, blank=True,)

# An entry for the users availability. All fields required, connected to an account
class Availability(models.Model):
	MONDAY = 'mon'
	TUESDAY = 'tue'
	WEDNESDAY = 'wed'
	THURSDAY = 'thu'
	FRIDAY = 'fri'
	SATURDAY = 'sat'
	SUNDAY = 'sun'

	PREF_DAY_CHOICES = (
		(MONDAY, 'Monday'),
		(TUESDAY, 'Tuesday'),
		(WEDNESDAY, 'Wednesday'),
		(THURSDAY, 'Thursday'),
		(FRIDAY, 'Friday'),
		(SATURDAY, 'Saturday'),
		(SUNDAY, 'Sunday'),
	)

	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	start_time = models.TimeField(null=False, blank=False)
	end_time = models.TimeField(null=False, blank=False)

	pref_day = models.CharField(
		max_length=3,
		choices=PREF_DAY_CHOICES,
		default=MONDAY,
	)

	competitive = models.BooleanField(default=False)

# An entry for a game that we support
class Game(models.Model):
	name = models.CharField(
		max_length=20,
		null=False,
		blank=False,
	)

	max_players = models.IntegerField(
		null=False,
		blank=False,
		default='2',
	)

	description = models.CharField(
		max_length=255,
		null=False,
		blank=False,
		default='No description provided.',
	)

# Each game we have needs a standard method of getting rank.
class Game_Api_Connection(models.Model):
	game = models.OneToOneField('Game', on_delete=models.PROTECT,)
	# This url should contain a tag that includes <User_ID> that will be replaced when making a request.
	api_url = models.CharField(max_length=255, null=False, blank=False,)
	# What the JSON representation of competitive rank is called for this API
	comp_json = models.CharField(max_length=15, null=False, blank=False,)
	# What the JSON representation of casual rank is called for this API
	cas_json = models.CharField(max_length=15, null=False, blank=False,)


# An entry for a Role that has a connected game
class Game_Role(models.Model):
	game = models.ForeignKey(
		'Game',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	name = models.CharField(
		max_length=20,
		blank=False,
		null=False,
	)

	description = models.CharField(
		max_length=255,
		null=False,
		blank=False,
		default='No description provided.',
	)

# A game account that a user has connected to their account
class Profile_Connected_Game_Account(models.Model):
	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	game_api = models.ForeignKey(
		'Game_Api_Connection',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	# The ID that we should use to request the players details.
	game_player_name = models.CharField(max_length=50, blank=False, null=False, default='<Missing>')
	cas_rank = models.IntegerField(blank=True, null=True, default=0,)
	comp_rank = models.IntegerField(blank=True, null=True, default=0,)

# An entry for a Session, created when two players queue that could match, then players that match are added when possible
class Session(models.Model):
	game = models.ForeignKey(
		'Game',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	datetime_created = models.DateTimeField(auto_now_add=True,)
	start_time = models.TimeField(blank=True, null=True,)
	end_time = models.TimeField(blank=True, null=True,)

# An entry for a profile's session, connected with a Session when it is found
class Session_Profile(models.Model):
	session = models.ForeignKey(
		'Session',
		on_delete=models.PROTECT,
		blank=True,
		null=True,
	)

	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	game_role = models.ForeignKey(
		'Game_Role',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

# An entry for a report that a player has made.
class Report(models.Model):
	TOXICITY = 'toxic'
	SPORTSMANSHIP = 'sportsmanship'

	REPORT_REASON_CHOICES = (
		(TOXICITY, 'Toxicity'),
		(SPORTSMANSHIP, 'Unsportsmanlike Behaviour'),
	)

	session = models.ForeignKey(
		'Session',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	user_reported = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
		related_name='user_reported_report',
	)

	sent_by = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
		related_name='sent_by_report',
	)

	report_reason = models.CharField(
		max_length=15,
		choices=REPORT_REASON_CHOICES,
		default=TOXICITY,
	)

	datetime_sent = models.DateTimeField(auto_now_add=True,)

