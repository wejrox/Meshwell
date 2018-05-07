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
		return self.user.username

	USWEST = 'US-West'
	USEAST = 'US-East'
	EUROPE = 'Europe'
	OCEANIA = 'Oceania'
	ASIA = 'Asia'
	SOUTHAMERICA = 'South America'
	SOUTHAFRICA = 'South Africa'
	MIDDLEEAST = 'Middle-East'

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

	# Weighting of commends
	commend_priority_1 = models.CharField(null=False, blank=False, max_length=20, default=TEAMWORK, choices=COMMENDS_CHOICES,)
	commend_priority_2 = models.CharField(null=False, blank=False, max_length=20, default=COMMUNICATION, choices=COMMENDS_CHOICES,)
	commend_priority_3 = models.CharField(null=False, blank=False, max_length=20, default=SKILL, choices=COMMENDS_CHOICES,)
	commend_priority_4 = models.CharField(null=False, blank=False, max_length=20, default=SPORTSMANSHIP, choices=COMMENDS_CHOICES,)

	# Other details
	birth_date = models.DateField(null=True, blank=False,)
	sessions_played = models.IntegerField(null=False, blank=False, default=0,)
	received_ratings = models.IntegerField(null=False, blank=False, default=0,)
	in_queue = models.BooleanField(null=False, blank=False, default=False,)

	# The users id on discord, which will never change. Current max length is 19, but set to 20 for safe measure (64bit Integer)
	discord_id = models.CharField(max_length=20, null=True, blank=True,)

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
		default=2,
	)

	description = models.CharField(
		max_length=255,
		null=False,
		blank=False,
		default='No description provided.',
	)
	# ADD IMAGE SUPPORT
	image = models.ImageField(
		upload_to="games",
		default='games/default.png',
	)

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

	PS4 = 'Playstation 4'
	XBOX = 'Xbox One'
	PC = 'PC'

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
		max_length=20,
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
		return str.join(', ', (str(self.game.name), str(self.datetime_created), str(self.start)))

	game = models.ForeignKey(
		'Game',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
	)

	datetime_created = models.DateTimeField(auto_now_add=True,)
	start = models.DateTimeField(blank=True, null=True,)
	end_time = models.TimeField(blank=True, null=True,)
	competitive = models.BooleanField(default=False,)
	space_available = models.BooleanField(default=True,)

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

	rating = models.IntegerField(blank=True, null=True)

# An entry for a report that a player has made.
class Report(models.Model):
	def __str__(self):
		return str.join(str(self.user_reported), str(self.datetime_sent))

	TOXICITY = 'Toxicity'
	SPORTSMANSHIP = 'Poor sportsmanship'

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
		max_length=255,
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

#Banned Users model
class Banned_User(models.Model):
	def __str__(self):
		return self.user.get_username

	profile = models.ForeignKey(
		'Profile',
		on_delete=models.PROTECT,
		blank=False,
		null=False,
		related_name='banned_profile'
	)

	report_reason = models.ForeignKey(
		'report',
		on_delete=models.PROTECT,
		blank=True,
		null=True,
	)

	date_banned = models.DateField(null=True, blank=False,)
