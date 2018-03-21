from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from mysite.serializers import UserSerializer, GroupSerializer
from django.http import HttpResponse
from django.shortcuts import render
import requests

# The current sample index page, which makes requests to the API, and passes accross the information required.
def index(request):
	# Dummy data
	user_pk = 7
	# Build API call
	url = 'http://52.62.206.111/api/profile/' + str(user_pk) + '?format=json'
	# Call the api, store the response
	response = requests.get(url)
	# Parse the response into JSON format to be interpreted
	data = response.json()

	# Get what we need from the API response and give it to the context
	context = {
		'username':data['user']['username'],
		'first_name':data['user']['first_name'],
		'last_name':data['user']['last_name'],
		'pref_server':data['pref_server'],
	}

	# Give back the context to the index page
	return render(request, 'mysite/index.html', context)
