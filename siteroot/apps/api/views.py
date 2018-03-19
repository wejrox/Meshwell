from rest_framework import viewsets
from ..api.serializers import ProfileSerializer
from ..api.models import Profile

# API Methods
class ProfileViewSet(viewsets.ModelViewSet):
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer
