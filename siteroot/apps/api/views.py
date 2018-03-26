from rest_framework import viewsets
from ..api import serializers
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Game_Api_Connection, Feedback

# API Methods
class ProfileViewSet(viewsets.ModelViewSet):
	queryset = Profile.objects.all()
	serializer_class = serializers.ProfileSerializer

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

class Game_Api_ConnectionViewSet(viewsets.ModelViewSet):
	queryset = Game_Api_Connection.objects.all()
	serializer_class = serializers.Game_Api_ConnectionSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
	queryset = Feedback.objects.all()
	serializer_class = serializers.FeedbackSerializer
