from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
import requests
from mysite.forms import FeedbackForm
#from django.contrib import auth
from django.contrib.auth.views import login
from django.contrib.auth.forms import AuthenticationForm

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

#views for the profile page
def profile(request):
	#reference from index function
	user_pk = request.user
	url = 'http://52.62.206.111/api/profile/' + str(user_pk.id) + '?format=json'
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

# Login view
def login_view(request):
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request,user)
	else:
		form = AuthenticationForm()

	# Display form or validation
	context = {
		'form':form,
	}
	return render(request, 'mysite/login.html', context)

#views for the feedback form page
def feedback(request):
	title = 'Feedback'
	form = FeedbackForm(request.POST)
	context = {
		"title": title,
		"form": form
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

	else:
		form = FeedbackForm()

	context = {
		'title': "Feedback submittted! Thank You!"
	}
	return render(request, 'mysite/feedback.html', context)
