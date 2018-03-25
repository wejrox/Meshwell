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

# Index page/Landing page
def index(request):
	url = 'http://52.62.206.111/api/game/?format=json'
	response = requests.get(url)
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
		profile = Profile.objects.get(user=request.user.id)
		url = 'http://52.62.206.111/api/profile/' + str(profile.id) + '/?format=json'
		response = requests.get(url)
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
		context = {'message':'You must be logged in to view this page'}
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

			### printing the values of full_name, email, title, and email
			#for key, value in form.cleaned_data.iteritems():
			#print key, value

			full_name = form.cleaned_data.get("name")
			email = form.cleaned_data.get("email")
			title = form.cleaned_data.get("title")
			message = form.cleaned_data.get("message")

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
