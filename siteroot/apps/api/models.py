from django.db import models
from django.contrib.auth.models import User
# Auth
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# We are building on top of djangos default user model as it provides authentication already, adding our required fields for meshwell
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.PROTECT)

	def __str__(self):
		return self.user.username;

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
	in_queue = models.BooleanField(null=False, blank=False, default=False,)

	# The users name on discord, which is limited by them to 32 chars, plus 5 for id. e.g. myname#1205
	discord_name = models.CharField(max_length=37, null=True, blank=True,)

# Add a trigger for creating a profile if a user is created and the profile doesn't exist
# This handles user creation from the website, alongside user creation via api which creates both a user and an attached profile
@receiver(post_save, sender=User)
def create_profile(sender, instance=None, created=False, **kwargs):
	userprofile = Profile.objects.filter(user=instance)
	if created and not userprofile:
		profile = Profile.objects.create(user=instance)
		profile.save()

# Add a trigger for token authentication generation on user signup
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)

# An entry for the users availability. All fields required, connected to an account
class Availability(models.Model):
	def __str__(self):
		return str.join(str(self.start_time), str(self.end_time))

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

	start_time = models.TimeField(null=False, blank=False)
	end_time = models.TimeField(null=False, blank=False)

	pref_day = models.CharField(
		max_length=10,
		choices=PREF_DAY_CHOICES,
		default=MONDAY,
	)

	competitive = models.BooleanField(default=False)

# An entry for a game that we support
class Game(models.Model):
	def __str__(self):
		return self.name

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

# OBSELETE (NO LONGER IN USE, MANUALLY ADDED INSTEAD)
# Each game we have needs a standard method of getting rank.
class Game_Api_Connection(models.Model):
	game = models.OneToOneField('Game', on_delete=models.PROTECT,)

	def __str__(self):
		return self.game.name

	# This url should contain a tag that includes <User_ID> that will be replaced when making a request.
	api_url = models.CharField(max_length=255, null=False, blank=False,)
	# What the JSON representation of competitive rank is called for this API
	comp_json = models.CharField(max_length=15, null=False, blank=False,)
	# What the JSON representation of casual rank is called for this API
	cas_json = models.CharField(max_length=15, null=False, blank=False,)


# An entry for a Role that has a connected game
class Game_Role(models.Model):
	def __str__(self):
		return self.name

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
	def __str__(self):
		return self.game_player_tag

	PS4 = 'ps4'
	XBOX = 'xone'
	PC = 'pc'

	PLATFORM_CHOICES = (
		(PS4, 'Playstation 4'),
		(XBOX, 'Xbox One'),
		(PC, 'PC'),
	)

	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

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
		max_length=5,
		blank=False,
		null=False,
		choices=PLATFORM_CHOICES,
                default=PC,
	)
	cas_rank = models.IntegerField(blank=True, null=True, default=0,)
	comp_rank = models.IntegerField(blank=True, null=True, default=0,)

# An entry for a Session, created when two players queue that could match, then players that match are added when possible
class Session(models.Model):
	def __str__(self):
		return str.join(', ', (str(self.game.name), str(self.datetime_created), str(self.start_time)))

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
	def __str__(self):
		return str.join(str(self.profile), str(self.game_role))

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
		blank=True,
		null=True,
	)

# An entry for a report that a player has made.
class Report(models.Model):
	def __str__(self):
		return str.join(str(self.user_reported), str(self.datetime_sent))

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

# The feedback model for when a user submits feedback on the website
class Feedback(models.Model):
	def __str__(self):
		return self.title + ', ' + self.name

	name = models.CharField(max_length=120)
	email = models.EmailField()
	title = models.CharField(max_length=254)
	message = models.TextField()

class Rate_Session(models.Model):
	def __str__(self):
		return str.join('. ', (str(self.profile), str(self.session)))

	ONE = '1'
	TWO = '2'
	THREE = '3'
	FOUR = '4'
	FIVE = '5'

	RATING_CHOICES = (
		(ONE, '1'),
		(TWO, '2'),
		(THREE, '3'),
		(FOUR, '4'),
		(FIVE, '5'),
	)

	session = models.ForeignKey(
		'Session',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)
	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)
	rating = models.IntegerField(null=True, blank=True, default=3,)
	comments = models.TextField(null=True, blank=True, max_length=500)
