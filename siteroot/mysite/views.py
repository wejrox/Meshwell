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

#function based views with dummy data
def feedback(request):

	#Dummy Data
	context ={	
		'email':'abc@gmail.com',
		'full_name':'Jon DT',
		'title':'title',
		'message':'message',
	}
	return render(request, 'feedback.html', context)

def login(request):
	
	#Dummy Data
	context ={
		'username':'James123',
		'password':'abc123',
	}
	return render(request, 'login.html', context)

def profile(request):
	
	#Dummy Data
	context ={
		'username':'James123',
		'first_name':'James',
		'last_name':'McDowell',
		'email':'abc@gmail.com',
		'date_birth':'14/04/1995',
		'sessions_played':'5',
	}
	return render(request, 'profile.html', context)
