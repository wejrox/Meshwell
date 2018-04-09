from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from ..api import serializers
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Game_Api_Connection, Feedback

# API Methods
class ProfileViewSet(viewsets.ModelViewSet):
	queryset = Profile.objects.all()
	serializer_class = serializers.ProfileSerializer
	filter_backends = (DjangoFilterBackend,)

class AvailabilityViewSet(viewsets.ModelViewSet):
	queryset = Availability.objects.all()
	serializer_class = serializers.AvailabilitySerializer

class GameViewSet(viewsets.ModelViewSet):
	queryset = Game.objects.all()
	serializer_class = serializers.GameSerializer

class Game_RoleViewSet(viewsets.ModelViewSet):
	queryset = Game_Role.objects.all()
	serializer_class = serializers.Game_RoleSerializer

class SessionViewSet(viewsets.ModelViewSet):
	queryset = Session.objects.all()
	serializer_class = serializers.SessionSerializer

class Session_ProfileViewSet(viewsets.ModelViewSet):
	queryset = Session_Profile.objects.all()
	serializer_class = serializers.Session_ProfileSerializer

class ReportViewSet(viewsets.ModelViewSet):
	queryset = Report.objects.all()
	serializer_class = serializers.ReportSerializer

class Profile_Connected_Game_AccountViewSet(viewsets.ModelViewSet):
	queryset = Profile_Connected_Game_Account.objects.all()
	serializer_class = serializers.Profile_Connected_Game_AccountSerializer
	def get_queryset(self):
		queryset = Profile_Connected_Game_Account.objects.all()
		profile = self.request.query_params.get('profile')
		id = self.request.query_params.get('id')
		game = self.request.query_params.get('game')
		# If given an id there can only be 1 response
		if id is not None:
			queryset = Profile_Connected_Game_Account.get(id=str(id))
			return queryset
		# If given a profile there may be many responses
		if profile is not None:
			queryset = queryset.filter(profile__id=int(profile))
		# Ir given a game there may be many responses
		if game is not None:
			queryset = queryset.filter(game__name=game)
		return queryset


class Game_Api_ConnectionViewSet(viewsets.ModelViewSet):
	queryset = Game_Api_Connection.objects.all()
	serializer_class = serializers.Game_Api_ConnectionSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
	queryset = Feedback.objects.all()
	serializer_class = serializers.FeedbackSerializer
