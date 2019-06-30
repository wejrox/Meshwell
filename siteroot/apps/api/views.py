from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from ..api import serializers
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Feedback,Banned_User

'''
Methods available to the ReST API.
'''


class ProfileViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all user profiles based on the serialiser created.
	'''
	queryset = Profile.objects.all()
	serializer_class = serializers.ProfileSerializer
	filter_backends = (DjangoFilterBackend,)


class AvailabilityViewSet(viewsets.ModelViewSet):
	'''
	Gets all availabilities, filtered on profile if provided.
	'''
	queryset = Availability.objects.all()
	serializer_class = serializers.AvailabilitySerializer


	def get_queryset(self):
		'''
		Returns all availabilities, filtered on profile if provided.
		'''
		queryset = Availability.objects.all()
		profile = self.request.query_params.get('profile')
		if profile is not None:
			queryset = queryset.filter(profile__id=int(profile))

		return queryset


class GameViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all games based on the serialiser created.
	'''
	queryset = Game.objects.all()
	serializer_class = serializers.GameSerializer


class Game_RoleViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all game roles based on the serialiser created.
	'''
	queryset = Game_Role.objects.all()
	serializer_class = serializers.Game_RoleSerializer


class SessionViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all sessions based on the serialiser created.
	'''
	queryset = Session.objects.all()
	serializer_class = serializers.SessionSerializer


class Session_ProfileViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all session profiles based on the serialiser created.
	'''
	queryset = Session_Profile.objects.all()
	serializer_class = serializers.Session_ProfileSerializer


class ReportViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all reports based on the serialiser created.
	'''
	queryset = Report.objects.all()
	serializer_class = serializers.ReportSerializer


class Profile_Connected_Game_AccountViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all profile connected game accounts based on the serialiser created.
	'''
	queryset = Profile_Connected_Game_Account.objects.all()
	serializer_class = serializers.Profile_Connected_Game_AccountSerializer


	def get_queryset(self):
		'''
		Returns either the instance with the id provided, or filters all instances based on the profile and game attached.
		If no parameters have been given, returns all instances.
		'''
		queryset = Profile_Connected_Game_Account.objects.all()
		profile = self.request.query_params.get('profile')
		id = self.request.query_params.get('id')
		game = self.request.query_params.get('game')

		# If given an id there can only be 1 response.
		if id is not None:
			queryset = Profile_Connected_Game_Account.get(id=str(id))
			return queryset

		# If given a profile there may be many responses.
		if profile is not None:
			queryset = queryset.filter(profile__id=int(profile))

		# If given a game there may be many responses.
		if game is not None:
			queryset = queryset.filter(game__name=game)
		return queryset


class FeedbackViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all feedback submissions based on the serialiser created.
	'''
	queryset = Feedback.objects.all()
	serializer_class = serializers.FeedbackSerializer


class Banned_UserViewSet(viewsets.ModelViewSet):
	'''
	Gets details of all banned users based on the serialiser created.
	'''
	queryset = Banned_User.objects.all()
	serializer_class = serializers.Banned_UserSerializer
