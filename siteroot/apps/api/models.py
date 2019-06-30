from django.db import models
from django.contrib.auth.models import User
# Auth.
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# We are building on top of djangos default user model as it provides authentication already, adding our required fields for meshwell.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.PROTECT)

	def __str__(self):
		return self.user.username

	# Regions that players can reside within.
	USWEST = 'US-West'
	USEAST = 'US-East'
	EUROPE = 'Europe'
	OCEANIA = 'Oceania'
	ASIA = 'Asia'
	SOUTHAMERICA = 'South America'
	SOUTHAFRICA = 'South Africa'
	MIDDLEEAST = 'Middle-East'

	# Choices for regions that a player would like to queue in.
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
		max_length=20,
		choices=PREF_SERVER_CHOICES,
		default=USWEST,
	)

	# Types of attributes that a user can be commended for.
	TEAMWORK = 'Teamwork'
	COMMUNICATION = 'Communication'
	SKILL = 'Skill'
	SPORTSMANSHIP = 'Sportsmanship'

	COMMENDS_CHOICES = (
		(TEAMWORK, 'Teamwork'),
		(COMMUNICATION, 'Communication'),
		(SKILL, 'Skill'),
		(SPORTSMANSHIP, 'Sportsmanship'),
	)
	teamwork_commends = models.IntegerField(null=False, blank=False, default='0',)
	communication_commends = models.IntegerField(null=False, blank=False, default='0',)
	skill_commends = models.IntegerField(null=False, blank=False, default='0',)
	sportsmanship_commends = models.IntegerField(null=False, blank=False, default='0',)

	# Weighting of commends.
	commend_priority_1 = models.CharField(null=False, blank=False, max_length=20, default=TEAMWORK, choices=COMMENDS_CHOICES,)
	commend_priority_2 = models.CharField(null=False, blank=False, max_length=20, default=COMMUNICATION, choices=COMMENDS_CHOICES,)
	commend_priority_3 = models.CharField(null=False, blank=False, max_length=20, default=SKILL, choices=COMMENDS_CHOICES,)
	commend_priority_4 = models.CharField(null=False, blank=False, max_length=20, default=SPORTSMANSHIP, choices=COMMENDS_CHOICES,)
	ignore_matchmaking = models.BooleanField(null=False, blank=False, default=False,)

	# The default game type to prefer when matching.
	pref_game = models.ForeignKey(
		'Game',
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)

	# Other user details.
	birth_date = models.DateField(null=True, blank=False,)
	sessions_played = models.IntegerField(null=False, blank=False, default=0,)
	received_ratings = models.IntegerField(null=False, blank=False, default=0,)
	in_queue = models.BooleanField(null=False, blank=False, default=False,)

	# The users id on discord, which will never change. Current max length is 19, but set to 20 for safe measure (64bit Integer).
	discord_id = models.CharField(max_length=20, null=True, blank=True,)


@receiver(post_save, sender=User)
def create_profile(sender, instance=None, created=False, **kwargs):
	'''
	A trigger for creating a profile if a user is created and the profile doesn't exist.
	This handles user creation from the website, alongside user creation via api which creates both a user and an attached profile.
	'''
	userprofile = Profile.objects.filter(user=instance)
	if created and not userprofile:
		profile = Profile.objects.create(user=instance)
		profile.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	'''
	A trigger for token authentication generation on user signup.
	'''
	if created:
		Token.objects.create(user=instance)


class Availability(models.Model):
	'''
	An entry for the users availability. All fields required, connected to an account.
	'''
	def __str__(self):
		return str.join(str(self.start_time), str(self.end_time))

	# Days of the week.
	MONDAY = 'Monday'
	TUESDAY = 'Tuesday'
	WEDNESDAY = 'Wednesday'
	THURSDAY = 'Thursday'
	FRIDAY = 'Friday'
	SATURDAY = 'Saturday'
	SUNDAY = 'Sunday'

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

	# Preferred time slot on the day to play in.
	start_time = models.TimeField(null=False, blank=False)
	end_time = models.TimeField(null=False, blank=False)

	pref_day = models.CharField(
		max_length=10,
		choices=PREF_DAY_CHOICES,
		default=MONDAY,
	)

	# Whether or not this preference is for competitive (ranked) play.
	competitive = models.BooleanField(default=False)


class Game(models.Model):
	'''
	An entry for a game that we support.
	'''
	def __str__(self):
		return self.name

	# Name of the game.
	name = models.CharField(
		max_length=20,
		null=False,
		blank=False,
	)

	# Maximum number of players able to join a session of this game.
	max_players = models.IntegerField(
		null=False,
		blank=False,
		default=2,
	)

	# Description of the game.
	description = models.CharField(
		max_length=255,
		null=False,
		blank=False,
		default='No description provided.',
	)

	# An image describing the game (usually box-art).
	image = models.ImageField(
		upload_to="games",
		default='games/default.png',
	)


class Game_Role(models.Model):
	'''
	An entry for a Role to play in a game, which has a connected game.
	'''
	def __str__(self):
		return self.name

	# Game that this role belongs to.
	game = models.ForeignKey(
		'Game',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	# Name of the role.
	name = models.CharField(
		max_length=20,
		blank=False,
		null=False,
	)

	# What the role entails.
	description = models.CharField(
		max_length=255,
		null=False,
		blank=False,
		default='No description provided.',
	)


class Profile_Connected_Game_Account(models.Model):
	'''
	A game account that a user has connected to their meshwell account.
	'''
	def __str__(self):
		return self.game_player_tag

	# Supported platforms.
	PS4 = 'Playstation 4'
	XBOX = 'Xbox One'
	PC = 'PC'

	PLATFORM_CHOICES = (
		(PS4, 'Playstation 4'),
		(XBOX, 'Xbox One'),
		(PC, 'PC'),
	)

	# Meshwell profile connected to this game account.
	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	# Game which this account belongs to.
	game = models.ForeignKey(
		'Game',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
		default=1,
	)

	# The ID that we should use to request the players details.
	game_player_tag = models.CharField(max_length=50, blank=False, null=False, default='<Missing>')
	platform = models.CharField(
		max_length=20,
		blank=False,
		null=False,
		choices=PLATFORM_CHOICES,
		default=PC,
	)

	# Casual rank.
	cas_rank = models.IntegerField(blank=True, null=True, default=0,)

	# Competitive rank.
	comp_rank = models.IntegerField(blank=True, null=True, default=0,)


class Session(models.Model):
	'''
	An entry for a Session, created when two players queue that could match, then players that match are added when possible.
	'''
	def __str__(self):
		return str.join(', ', (str(self.game.name), str(self.datetime_created), str(self.start)))

	# Game that is selected for this session.
	game = models.ForeignKey(
		'Game',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	# Datetime that the session was created (defaults to the current datetime).
	datetime_created = models.DateTimeField(auto_now_add=True,)

	# Datetime that the session will begin.
	start = models.DateTimeField(blank=True, null=True,)

	# Datetime that the session will end.
	end_time = models.TimeField(blank=True, null=True,)

	# Whether or not this session is competitive.
	competitive = models.BooleanField(default=False,)

	# Whether or not this session has space available.
	space_available = models.BooleanField(default=True,)


class Session_Profile(models.Model):
	'''
	An entry for a profile's session, connected with a Session when it is found.
	'''
	def __str__(self):
		return str.join(str(self.profile), str(self.game_role))

	# Session which a profile is connected to.
	session = models.ForeignKey(
		'Session',
		on_delete=models.PROTECT,
		blank=True,
		null=True,
	)

	# Profile that has joined a session.
	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	# Selected game role of the profile.
	game_role = models.ForeignKey(
		'Game_Role',
		on_delete=models.PROTECT,
		blank=True,
		null=True,
	)

	# Meshwell rating of the profile.
	rating = models.IntegerField(blank=True, null=True)


class Report(models.Model):
	'''
	An entry for a report that a player has made.
	'''
	def __str__(self):
		return str.join(str(self.user_reported), str(self.datetime_sent))

	# Reason choices for reporting a player.
	TOXICITY = 'Toxicity'
	SPORTSMANSHIP = 'Poor sportsmanship'

	REPORT_REASON_CHOICES = (
		(TOXICITY, 'Toxicity'),
		(SPORTSMANSHIP, 'Unsportsmanlike Behaviour'),
	)

	# Session which the report occured within.
	session = models.ForeignKey(
		'Session',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	# Profile that was reported.
	user_reported = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
		related_name='user_reported_report',
	)

	# User that reported the profile.
	sent_by = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
		related_name='sent_by_report',
	)

	# Reason given for reporting the profile.
	report_reason = models.CharField(
		max_length=255,
		choices=REPORT_REASON_CHOICES,
		default=TOXICITY,
	)

	# Datetime the report was sent.
	datetime_sent = models.DateTimeField(auto_now_add=True,)


class Feedback(models.Model):
	'''
	The feedback model for when a user submits feedback on the website.
	'''
	def __str__(self):
		return self.title + ', ' + self.name

	# Name of the person submitting feedback.
	name = models.CharField(max_length=120)

	# Contact email of the person submitting feedback.
	email = models.EmailField()

	# Title of the feedback message.
	title = models.CharField(max_length=254)

	# Contents of the feedback message.
	message = models.TextField()


class Banned_User(models.Model):
	'''
	An entry for users who have been banned from the Meshwell service.
	'''
	def __str__(self):
		return str.join(str(self.profile), str(self.report_reason.report_reason))

	# Profile which is banned.
	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
		related_name='banned_profile'
	)

	# Reason(s) why the profile was banned.
	report_reason = models.ManyToManyField(
		'Report',
		blank=True,
	)

	# Date that the ban commenced.
	date_banned = models.DateField(null=True, blank=False,)
