from rest_framework import viewsets
from ..api.serializers import ProfileSerializer, AvailabilitySerializer, GameSerializer, Game_RoleSerializer, SessionSerializer, Session_ProfileSerializer, ReportSerializer
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report

# API Methods
class ProfileViewSet(viewsets.ModelViewSet):
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer

class AvailabilityViewSet(viewsets.ModelViewSet):
	queryset = Availability.objects.all()
	serializer_class = AvailabilitySerializer

class GameViewSet(viewsets.ModelViewSet):
	queryset = Game.objects.all()
	serializer_class = GameSerializer

class Game_RoleViewSet(viewsets.ModelViewSet):
	queryset = Game_Role.objects.all()
	serializer_class = Game_RoleSerializer

class SessionViewSet(viewsets.ModelViewSet):
	queryset = Session.objects.all()
	serializer_class = SessionSerializer

class Session_ProfileViewSet(viewsets.ModelViewSet):
	queryset = Session_Profile.objects.all()
	serializer_class = Session_ProfileSerializer

class ReportViewSet(viewsets.ModelViewSet):
	queryset = Report.objects.all()
	serializer_class = ReportSerializer
