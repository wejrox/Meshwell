from django.contrib.auth.models import User, Group
from apps.api.models import Profile
from rest_framework import viewsets
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import requests
import json
from mysite.forms import FeedbackForm, DeactivateUser, RegistrationForm, EditProfileForm, UserPreferenceForm, ConnectAccountForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# Import settings
from django.conf import settings

# Method to get data from INTERNAL API (Meshwell API)
# Takes a table name, and parameters in the form of 'username=root' or similar
def retrieve_data(table, *params):
	url = 'http://127.0.0.1/api/'+table+'/?format=json'
	# Add the additional parameters
	for string in params:
		url += '&'+string

	headers = { 'Authorization':'Token ' + settings.API_TOKEN }
	response = requests.get(url, headers=headers)
	if response.ok:
		data = response.json()
		return data
	return None

# Deletes data from the database using the INTERNAL API (Meshwell API)
# Takes a table name, and an entry id (pk)
def delete_data(url):
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }
	response = requests.delete(url, headers=headers)

	if response.ok:
		print('deleted the entry')
		return True
	else:
		print('couldn\'t unlink the entry')
		print(response.status_code)
		return False

# Index page/Landing page
def index(request):
	data = retrieve_data('game')

	context = {'games':{}}
	for game in data:
		g = { 'name':game['name'], 'description':game['description'] }
		context['games'][game['name']] = g

	# Give back the context to the index page
	return render(request, 'mysite/index.html', context)

# User dashboard
@login_required
def dashboard(request):
	context = {
		'title':'Dashboard',
		'message':'This is a stub page for the dashboard. No functionality has been added yet.',
	}

	data = retrieve_data('profile', 'id=2')
	print(data)
	return render(request, 'mysite/dashboard.html', context)

#views for the profile page
@login_required
def profile(request):
	#reference from index function
	if request.user.is_authenticated:
		# Just in case a user somehow doesn't have a profile
		try:
			profile = request.user.profile
		except ObjectDoesNotExist:
			profile = Profile.objects.create(user=request.user)
			profile.save()

		data = retrieve_data('profile/'+str(profile.id))

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

# Catalog of games
def catalog(request):
	context = {
		'title':'Games Catalog',
		'message':'This is a stub page for our games catalog. No functionality has been added yet.',
	}
	return render(request, 'mysite/catalog.html', context)

# About us
def about_us(request):
	context = {
		'title':'About Us',
		'message':'This is a stub page for the about us page. No functionality has been added yet.',
	}
	return render(request, 'mysite/about_us.html', context)

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
		form = EditProfileForm(instance=request.user)
		context = { 'form':form, }
		return render(request, 'mysite/edit_profile.html', context)

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
			user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
			# User details entered must be the user that is logged in
			if request.user == user:
				user.is_active = False
				user.save()

				context = {
					'title': 'Account Deactivated',
					'message': 'Your account has been deactivated',
					'success': 'True',
				}
				return render(request, 'registration/deactivate_success.html', context)
			else:
				return redirect('index')
	# Show the deactivate page again if the form is invalid or if no form was posted
	return render(request, 'registration/deactivate.html', context)

@login_required
def connect_account(request):
	form = ConnectAccountForm()
	context = {
		'title':'Connect Game Account',
		'form':form,
	}

	if request.method == 'POST':
		form = ConnectAccountForm(request.POST)
		if form.is_valid():
			ranks = None
			# Get the rank depending on which game was selected
			if form.cleaned_data['game'].name == 'Rainbow Six Siege':
				# Ensure profile's game doesn't already have an account connected to it
				connected_account = retrieve_data('profile_connected_game_account', 'profile='+str(request.user.profile.id))
				if not connected_account:
					ranks = get_r6siege_ranks(request, form.cleaned_data['game_player_tag'])
				else:
					context['error'] = 'You already have an account connected for this game.'
					return render(request, 'registration/connect_account.html', context)

			# Create a new instance so long as we found some ranks
			if ranks is not None:
				# Create a new instance from the form
				instance = form.save(commit=False)
				instance.profile = request.user.profile
				instance.cas_rank = ranks['cas_rank']
				instance.comp_rank = ranks['comp_rank']
				instance.save()

				return redirect('connected_accounts')
			else:
				context['error'] = 'The account name you have entered does not exist'
				return render(request, 'registration/connect_account.html', context)
		else:
			return render(request, 'registration/connect_account.html', context)

	else:
		return render(request, 'registration/connect_account.html', context)

	return render(request, 'registration/connect_account.html', context)

@login_required
def connected_accounts(request):
	data = retrieve_data('profile_connected_game_account', 'profile='+str(request.user.profile.id))
	games = retrieve_data('game')
	# Headers needed since we have to get the game name still
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }

	# Pre-create the games that we have
	final_data = {}
	for game in games:
		final_data[game['name']] = {}
		final_data[game['name']]['game_name'] = game['name']

	# Set each account to be inside the game if it exists
	if data is not None:
		for account in data:
			response = requests.get(account['game'], headers=headers)
			game_data = response.json()
			for entry in final_data:
				print(entry)
				if game_data['name'] == entry['game_name']:
					entry['game_player_tag'] = account['game_player_tag']
					entry['platform'] = account['platform']
					entry['cas_rank'] = account['cas_rank']
					entry['comp_rank'] = account['comp_rank']
					entry['connected'] = True

	context = { 'games':games, 'accounts':final_data, }

	if(request.GET.get('Unlink Account')):
		unlink_account(request.user.profile, request.GET.get('game'))

	return render(request, 'mysite/connected_accounts.html', context)

@login_required
def unlink_account(profile, game_name):
	print('unlinking account')
	# Get the record to delete
	record = retrieve_data('profile_connected_game_account', 'profile='+str(profile.id), 'game='+game_name)
	delete_data(record[0]['url'])

@login_required
def get_r6siege_ranks(request, player_tag):
	url = 'https://r6db.com/api/v2/players?name=' + player_tag
	headers = { 'X-App-Id':'MyRequest' }
	response = requests.get(url, headers=headers)
	data = response.json()
	print(player_tag)
	# Cancel the check if the user was not found or too many were found
	if not response.ok or len(data) > 1:
		return None

	# Decide which region to check
	region = request.user.profile.pref_server
	if region == 'oce' or region == 'as' or region == 'me':
		region = 'apac'
	elif region == 'saf' or region == 'usw' or region == 'use':
		region = 'ncsa'
	elif region == 'eu' or region == 'saf':
		region = 'emea'

	ranks = { 'cas_rank':0, 'comp_rank':0 }

	ranks['cas_rank'] = 0
	ranks['comp_rank'] = data[0]['ranks'][region]['mmr']

	return ranks

@login_required
def user_preference(request):
	form = UserPreferenceForm()
	context = {
		'title': 'User Preference',
		'message': 'Please enter your preference details.',
		'success': 'False',
		'form': form,
	}
	if request.user.is_authenticated:
		if request.method == 'POST':
			form = UserPreferenceForm(request.POST)

			if form.is_valid():
				form.save()
				context = {
					'title': 'Preference created.',
					'message': 'Your preference is created.',
					'success': 'True',
				}
				return render(request, 'registration/preference_success.html', context)
			else:
				form = UserPreferenceForm()
				return render(request, 'registration/preference.html', context)
		else:
			form = UserPreferenceForm()
			return render(request, 'registration/preference.html', context)
	else:
		context = {'error_title':'Not logged in', 'message':'You must be logged in to view this page'}
		return render(request, 'mysite/error_page.html', context)

