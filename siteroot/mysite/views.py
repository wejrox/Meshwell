from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from mysite.serializers import UserSerializer, GroupSerializer
from django.http import HttpResponse
from django.shortcuts import render

# Views for the meshwell site
def index(request):
	context = {
		'username':'James',
	}
	return render(request, 'index.html', context)
