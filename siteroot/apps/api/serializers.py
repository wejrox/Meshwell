from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth import validators
from django.forms import ValidationError
from django.db import IntegrityError
from django.utils.translation import gettext as _
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Game_Api_Connection, Feedback
from django.contrib.auth.hashers import check_password, make_password

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'password', 'date_joined', 'last_login', 'first_name', 'last_name', 'email', 'groups', 'is_staff', 'is_active', 'is_superuser')
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
		fields = '__all__' #('url', 'user', 'pref_server', 'birth_date', 'sessions_played', 'teamwork_commends', 'positivity_commends', 'skill_commends', 'communication_commends')

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

		# Create password hash
		# Set user details
		user.username = user_data.get('username', user.username)
		user.password = make_password(user_data.get('password', user.password))
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
		# Only set new password if password changed
		if not check_password(user_data.get('password'), user.password):
			user.password = make_password(user_data.get('password', user.password))
		user.email = user_data.get('email', user.email)
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)

		# Update groups if any have been selected
		group_name = user_data.get('groups', user.groups)
		if group_name:
			user_group = Group.objects.get(name=group_name[0])
			user_group.user_set.add(user)

		# Save to database
		instance.save()
		user.save()

		return instance

class AvailabilitySerializer(serializers.HyperlinkedModelSerializer):
	profile = ProfileSerializer(required='True')
	class Meta:
		model = Availability
		fields = '__all__'


class GameSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Game
		fields = '__all__'

class Game_RoleSerializer(serializers.HyperlinkedModelSerializer):
	game = GameSerializer(required='Truue')
	class Meta:
		model = Game_Role
		fields = '__all__'

class SessionSerializer(serializers.HyperlinkedModelSerializer):
	game = GameSerializer(required='True')
	class Meta:
		model = Session
		fields = '__all__'

class Session_ProfileSerializer(serializers.HyperlinkedModelSerializer):
	session = SessionSerializer(required='True')
	profile = ProfileSerializer(required='True')
	game_role = Game_RoleSerializer(required='True')
	class Meta:
		model = Session_Profile
		fields = '__all__'

class ReportSerializer(serializers.HyperlinkedModelSerializer):
	session = SessionSerializer(required='True')
	class Meta:
		model = Report
		fields = '__all__'

class Game_Api_ConnectionSerializer(serializers.HyperlinkedModelSerializer):
	game = GameSerializer(required='True')

	class Meta:
		model = Game_Api_Connection
		fields = '__all__'


class Profile_Connected_Game_AccountSerializer(serializers.HyperlinkedModelSerializer):
	profile = ProfileSerializer(required='True')
	game_api = Game_Api_ConnectionSerializer(required='True')
	class Meta:
		model = Profile_Connected_Game_Account
		fields = '__all__'

class FeedbackSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Feedback
		fields = '__all__'
