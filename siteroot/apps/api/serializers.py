from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth import validators
from django.forms import ValidationError
from django.db import IntegrityError
from django.utils.translation import gettext as _
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'date_joined', 'first_name', 'last_name', 'groups',)
		extra_kwargs = {
            		'username': {'validators': [validators.UnicodeUsernameValidator]},
        	}

	def validate(self, data):
		if self.context['request']._request.method == 'POST':
			if User.objects.filter(username=data['username']):
				raise serializers.ValidationError('Username already exists')
		return data

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
	user = UserSerializer(required='True')

	class Meta:
		model = Profile
		fields = ('url', 'user', 'pref_server', 'birth_date', 'sessions_played', 'teamwork_commends', 'positivity_commends', 'skill_commends', 'communication_commends')

	# Create a new User and Profile
	def create(self, validated_data):
		# Create User object
		user_data = validated_data.pop('user')
		user = User.objects.create()

		# Groups must be set this way due to being unabel to set many-many relationships
		group_name = user_data.get('groups', user.groups)
		if group_name:
			user_group = Group.objects.get(name=group_name[0])
			user_group.user_set.add(user)

		# Set user details
		user.username = user_data.get('username', user.username)
		user.date_joined = user_data.get('date_joined', user.date_joined)
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)

		# Generate profile and save
		profile = Profile.objects.create(user=user, **validated_data)
		user.save()

		# Return the profile's details after creation
		return profile

	# Update the User and Profile
	def update(self, instance, validated_data):
		# Get user information
		user_data = validated_data.pop('user')
		user = instance.user

		# Update profile
		instance.pref_server = validated_data.get('pref_server', instance.pref_server)
		instance.birth_date = validated_data.get('birth_date', instance.birth_date)
		instance.sessions_played = validated_data.get('sessions_played', instance.sessions_played)
		instance.teamwork_commends = validated_data.get('teamwork_commends', instance.teamwork_commends)
		instance.positivity_commends = validated_data.get('positivity_commends', instance.positivity_commends)
		instance.skill_commends = validated_data.get('skill_commends', instance.skill_commends)
		instance.communication_commends = validated_data.get('communication_comments', instance.communication_commends)

		# Update user
		user.username = user_data.get('username', user.username)
		user.email = user_data.get('email', user.email)
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)

		# Update groups if any have been selected
		group_name = user_data.get('groups', user.groups)
		if group_name:
			user_group = Group.objects.get(name=group_name[0])
			user_group.user_set.add(user)

		# Save to database
		profile.save()
		user.save()

		return instance

class AvailabilitySerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Availability
		fields = ('profile', 'start_time', 'end_time', 'pref_day',)


class GameSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Game
		fields = ('name', 'max_players', 'description',)

class Game_RoleSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Game_Role
		fields = ('game', 'name', 'description',)

class SessionSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Session
		fields = ('game', 'time_created', 'time_commenced', 'time_completed',)

class Session_ProfileSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Session_Profile
		fields = ('session', 'profile', 'game_role',)

class ReportSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Report
		fields = ('session', 'user_reported', 'sent_by', 'time_sent', 'report_reason',)
