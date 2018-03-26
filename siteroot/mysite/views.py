from django.contrib.auth.models import User, Group
from apps.api.models import Profile
from rest_framework import viewsets
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
import requests
import json
from mysite.forms import FeedbackForm
from django.contrib.auth import logout
from django.contrib.auth.views import login
from django.contrib.auth.forms import AuthenticationForm
# Import settings
from django.conf import settings

# Index page/Landing page
def index(request):
	url = 'http://127.0.0.1/api/game/?format=json'
	headers = {'Authorization':'Token ' + settings.API_TOKEN}
	response = requests.get(url, headers=headers)
	data = response.json()

	context = {'games':{}}
	for game in data:
		g = { 'name':game['name'], 'description':game['description'] }
		context['games'][game['name']] = g

	# Give back the context to the index page
	return render(request, 'mysite/index.html', context)

#views for the profile page
def profile(request):
	#reference from index function
	if request.user.is_authenticated:
		headers = { 'Authorization':'Token ' + settings.API_TOKEN }
		profile = Profile.objects.get(user=request.user.id)
		url = 'http://127.0.0.1/api/profile/' + str(profile.id) + '/?format=json'
		response = requests.get(url, headers=headers)
		data = response.json()

		#Dummy Data
		context = {
			'username':data['user']['username'],
			'first_name':data['user']['first_name'],
			'last_name':data['user']['last_name'],
			'pref_server':data['pref_server'],
			'birth_date':data['birth_date'],
			'sessions_played':data['sessions_played'],
			'teamwork_commends':data['teamwork_commends'],
			'positivity_commends':data['positivity_commends'],
			'skill_commends':data['skill_commends'],
			'communication_commends':data['communication_commends'],
		}
		return render(request, 'mysite/profile.html', context)
	else:
		context = {'error_title':'Not logged in', 'message':'You must be logged in to view this page'}
		return render(request, 'mysite/error_page.html', context)

#views for the feedback form page
def feedback(request):
	title = 'Feedback'
	form = FeedbackForm(request.POST)
	context = {
		'title': title,
		'form': form,
		'message': 'Please enter your details and feedback below. Your feedack is greatly appreciated, and helps us to provide a better service!',
		'success': 'False',
	}
	if request.method == 'POST':
		if form.is_valid():
			#saving details from the feedback form
			instance = form.save(commit=False)
			instance.save()

			context = {
				'title': 'Feedback submittted',
				'message': 'Thank you for your feedback!',
				'success': 'True',
			}
			return render(request, 'mysite/feedback.html', context)
	else:
		return render(request, 'mysite/feedback.html', context)

# Logging out. Currently loads a page. Recommend logging out to open a popup box that the user must click 'OK' to and be redirected to index.
def logout(request):
	logout(request)


def deactivate_user(request):
	title = 'Deactivate User'
	form = DeactivateUser(request.POST)
	context = {
		'title': title,
		'message': 'Are you sure you want to Deactivate your account?',
		'success': 'False',
	}
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		
		if form.is_valid():
			user = authenticate(username=username, password=password)
			if user is not None:
				user.is_active = False
				user.save()
				
				context = {
					'title': 'Account Deactivated',
					'message': 'Your account has been deactivated',
					'success': 'True',
				}
				return render(request, 'mysite/index.html', context)
	else:
		form = DeactivateUser()
	context = {
		'form': form,
	}
	return render(request, 'mysite/deactivate_user.html', context)
	
	
	
	
	
	
	
	
