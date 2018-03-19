from rest_framework import serializers
from django.contrib.auth.models import User, Group
from ..api.models import Profile

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'date_joined', 'first_name', 'last_name', 'groups',)

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
	user = UserSerializer(required='True')

	class Meta:
		model = Profile
		fields = ('url', 'user', 'pref_server', 'birth_date', 'sessions_played', 'teamwork_commends', 'positivity_commends', 'skill_commends', 'communication_commends')

	# Create a new User and Profile
	def create(self, validated_data):
		# User
		user_data = validated_data.pop('user')
		user = User.objects.create()

		# Groups must be set this way for some reason
		group_name = user_data.get('groups', user.groups)
		if group_name:
			user_group = Group.objects.get(name=group_name[0])
			user_group.user_set.add(user)

		user.username = user_data.get('username', user.username)
		user.date_joined = user_data.get('date_joined', user.date_joined)
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)
		user.save()

		# Profile
		profile = Profile.objects.create(user=user, **validated_data)
		return profile

	# Update the User and Profile
	def update(self, instance, validated_data):
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
		instance.save()

		# Update user
		user.username = user_data.get('username', user.username)
		user.email = user_data.get('email', user.email)
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)

		# Update groups
		group_name = user_data.get('groups', user.groups)
		if group_name:
			user_group = Group.objects.get(name=group_name[0])
			user_group.user_set.add(user)

		user.save()
		return instance
