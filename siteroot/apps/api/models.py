from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# We are building on top of djangos default user model as it provides authentication already, adding our required fields for meshwell
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)

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

	birth_date = models.DateField(null=True, blank=True)
	sessions_played = models.IntegerField(null=False, blank=False, default='0')
	teamwork_commends = models.IntegerField(null=False, blank=False, default='0')
	communication_commends = models.IntegerField(null=False, blank=False, default='0')
	skill_commends = models.IntegerField(null=False, blank=False, default='0')
	positivity_commends = models.IntegerField(null=False, blank=False, default='0')
