from django.contrib.auth.models import User, Group
from apps.api.models import Profile
from rest_framework import viewsets
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import requests
import json
from mysite.forms import FeedbackForm, DeactivateUser
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from mysite.forms import RegistrationForm
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
@login_required
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

#views for the registration page
def register(request):
	# Ensure there is nobody logged in
	if request.user.is_authenticated:
		return redirect('index')

	title = 'Register'
	form = RegistrationForm(request.POST)

	if request.method =='POST':
		# Create the user
		if form.is_valid():
			user = form.save()
			user.refresh_from_db() #load profile created by register
			user.save()
			user.refresh_from_db()
			# Get username and password to log in with
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			# Set the profile birth_date to the one given
			profile = Profile.objects.get(user=user)
			profile.birth_date = form.cleaned_data.get('birth_date')
			profile.save()

			# Redirect to login page
			return redirect('login')
	else:
		# Recreate the form since we aren't posting
		form = RegistrationForm()
		# Send the form to the page and render it
		return render(request, 'registration/register.html', {'form':form})

	# Return the form if the form isn't valid but post was specified
	return render(request, 'registration/register.html', {'form':form})

#Views for Edit Profile page
@login_required
def edit_profile(request):
	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user)
		context = {
			'form':form,
		}

		if form.is_valid():
			form.save()
			return redirect(reverse('mysite/profile.html'))
		else:
			form = EditProfileForm(instance=request.user)
			return render(request, 'mysite/edit_profile.html', context)
	else:
		return redirect('index')

# Logging out. Currently loads a page. Recommend logging out to open a popup box that the user must click 'OK' to and be redirected to index.
@login_required
def logout(request):
	logout(request)

@login_required
def deactivate_user(request):
	form = DeactivateUser()
	context = {
		'title': 'Confirm Details',
		'message': 'Please enter your login details in order to confirm deactivation.',
		'success': 'False',
		'form': form,
	}
	if request.method == 'POST':
		form = DeactivateUser(request.POST)
		#using built-in Authentication Form
		#username = request.POST['username']
		#password = request.POST['password']

		if form.is_valid():
			# Authenticate the user details they entered
			user = authenticate(username=username, password=password)
			# User details entered must be the user that is logged in
			if request.user = user:
				user.is_active = False
				user.save()

				context = {
					'title': 'Account Deactivated',
					'message': 'Your account has been deactivated',
					'success': 'True',
				}
				return render(request, 'registration/deactivate_success.html', context)

	# Show the deactivate page again if the form is invalid or if no form was posted
	return render(request, 'registration/deactivate.html', context)
