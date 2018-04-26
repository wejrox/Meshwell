from apps.api.models import Profile, Profile_Connected_Game_Account, Availability, Session, Session_Profile, Game
from rest_framework import viewsets
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect
import requests, json, urllib.parse, datetime
from mysite.forms import FeedbackForm, DeactivateUser, RegistrationForm, EditProfileForm, ConnectAccountForm, UserAvailabilityForm, RateSessionForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import login as contrib_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django.core.signals import request_finished
from django.dispatch import receiver
from django.urls import reverse, resolve
# Import settings
from django.conf import settings

# Receiver to create a profile if the user doesn't have one for some reason
@receiver(user_logged_in)
def auto_profile(sender, request, user, **kwargs):
	profile = Profile.objects.filter(user=user.id).first()
	if not profile:
		profile = Profile.objects.create(user=user)

# Gets the object representation of a given url
def retrieve_obj(url):
	path = urllib.parse.urlparse(url).path
	resolved_func, unused_args, resolved_kwargs = resolve(path)
	return resolved_func.cls().get_queryset().get(id=resolved_kwargs['pk'])

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

# Gets data from API given the direct URL
def retrieve_data_url(url):
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }
	response = requests.get(url, headers=headers)
	if response.ok:
		data = response.json()
		return data
	return None

# Deletes data from the database using the INTERNAL API (Meshwell API)
# Takes an API url address to delete
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
	if data:
		for game in data:
			g = { 'name':game['name'], 'description':game['description'] }
			context['games'][game['name']] = g

	# Give back the context to the index page
	return render(request, 'mysite/index.html', context)

# Terms of Service
def tos(request):
	return render(request, 'mysite/tos.html')

# User dashboard
@login_required

""" BACKUP - Old dashboard code.
def dashboard(request):
	context = {
		'title':'Dashboard',
		'message':'Play Together. Mesh Well.',
	}

	context['connected_accounts'] = Profile_Connected_Game_Account.objects.filter(profile=request.user.profile)
	context['availabilities'] = Availability.objects.filter(profile=request.user.profile)
	context['prev_sessions'] = Session_Profile.objects.filter(profile=request.user.profile).exclude(session__isnull=True).order_by('-session__start')

	data = retrieve_data('profile', 'id='+str(request.user.profile.id))
	return render(request, 'mysite/dashboard.html', context)
"""

def dashboard(request):
	#Profile
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }
	profile = Profile.objects.filter(user=request.user.id).first()
	if not profile:
		profile = Profile.objects.create(user=request.user)
	url = 'http://127.0.0.1/api/profile/' + str(profile.id) + '/?format=json'
	response = requests.get(url, headers=headers)
	data = response.json()

	context = {
		'title':'Dashboard',
		'message':'Play Together. Mesh Well.',

		#Profile Context Items
		'username':data['user']['username'],
		'first_name':data['user']['first_name'],
		'last_name':data['user']['last_name'],
		'pref_server':data['pref_server'],
		'birth_date':data['birth_date'],
		'sessions_played':data['sessions_played'],
		'teamwork_commends':data['teamwork_commends'],
		'sportsmanship_commends':data['sportsmanship_commends'],
		'skill_commends':data['skill_commends'],
		'communication_commends':data['communication_commends'],
	}

	context['connected_accounts'] = Profile_Connected_Game_Account.objects.filter(profile=request.user.profile)
	context['availabilities'] = Availability.objects.filter(profile=request.user.profile)
	context['prev_sessions'] = Session_Profile.objects.filter(profile=request.user.profile).exclude(session__isnull=True).order_by('-session__start')

	data = retrieve_data('profile', 'id='+str(request.user.profile.id))
	return render(request, 'mysite/dashboard.html', context)

#views for the profile page
@login_required
def profile(request):
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }
	profile = Profile.objects.filter(user=request.user.id).first()
	if not profile:
		profile = Profile.objects.create(user=request.user)
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
		'sportsmanship_commends':data['sportsmanship_commends'],
		'skill_commends':data['skill_commends'],
		'communication_commends':data['communication_commends'],
	}
	return render(request, 'mysite/profile.html', context)

# CSS Standarisation Page
def css_standard(request):
	context = {
		'title':'CSS Standard',
	}
	return render(request, 'mysite/css_standard.html', context)

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
		'message': 'Please enter your details and feedback below. Your feedback is greatly appreciated, and helps us to provide a better service!',
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
		return redirect('dashboard')

	title = 'Register'
	if request.method =='POST':
		form = RegistrationForm(request.POST)
		# Create the user
		if form.is_valid():
			form.save()
			# Redirect to login page
			return redirect('login')
	else:
		# Recreate the form since we aren't posting
		form = RegistrationForm()

	# Return the form if the form isn't valid or user just entered page
	return render(request, 'registration/register.html', {'form':form, 'title':title})

#Views for Edit Profile page
@login_required
def edit_profile(request):
	context = {'title':'Edit Profile'}
	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user, profile=request.user.profile)

		if form.is_valid():
			form.save()
			return redirect('profile')
	else:
		form = EditProfileForm(instance=request.user, profile=request.user.profile)

	context['form'] = form
	return render(request, 'mysite/edit_profile.html', context)

# Login. Implemented here to prevent logged in users from accessing the page
def a_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('dashboard')
			else:
				return redirect('about-us')
		else:
			return render(request, 'registration/login.html', {})
	else:
		return render(request, 'registration/login.html', {})

# Logging out. Currently loads a page. Recommend logging out to open a popup box that the user must click 'OK' to and be redirected to index.
@login_required
def a_logout(request):
	logout(request)
	return redirect(reverse('index'))

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
	connected_accounts = retrieve_data('profile_connected_game_account', 'profile='+str(request.user.profile.id))
	games = retrieve_data('game')
	# Headers needed since we have to get the game name still
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }

	# Pre-create the games that we have
	final_data = {}
	for game in games:
		final_data[game['url']] = {}
		final_data[game['url']]['game_name'] = game['name']
		final_data[game['url']]['image'] = game['image']
		final_data[game['url']]['game_player_tag'] = 'Not Connected!'

	# Set each account to be inside the game if it exists
	if connected_accounts and games:
		# Assign each of the accounts by accessing related to game url
		for account in connected_accounts:
			final_data[account['game']]['game_player_tag'] = account['game_player_tag']
			final_data[account['game']]['platform'] = account['platform']
			final_data[account['game']]['cas_rank'] = account['cas_rank']
			final_data[account['game']]['comp_rank'] = account['comp_rank']
			final_data[account['game']]['connected'] = True


	context = { 'title':'Connected Accounts', 'accounts':final_data, }

	# User clicks unlink button
	if(request.GET.get('Unlink Account')):
		unlink_account(request.user.profile, request.GET.get('game'))
		return redirect('connected_accounts')

	return render(request, 'mysite/connected_accounts.html', context)

# Remove the record of the connected account
@login_required
def unlink_account(profile, game_name):
	record = retrieve_data('profile_connected_game_account', 'profile='+str(profile.id), 'game='+game_name)
	if record:
		delete_data(record[0]['url'])

# Gets the player details specified, or None if there are multiple entries
# Decides on region based on the profiles region. (Perhaps change later?)
@login_required
def get_r6siege_ranks(request, player_tag):
	url = 'https://r6db.com/api/v2/players?name=' + player_tag
	headers = { 'X-App-Id':'MyRequest' }
	response = requests.get(url, headers=headers)
	data = response.json()
	print(player_tag)
	# Cancel the check if the user was not found or too many were found
	if not response.ok or len(data) != 1:
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

# Handles the user entering the queue for a session when the button on the nav bar is pressed
@login_required
def enter_queue(request):
    # Get user details
    django_user = request.user
    user_profile = django_user.profile
    # Ensure player is not already queueing
    if user_profile.in_queue:
        return redirect('dashboard')

    # Create a user session
#    player_session = Session_Profile.objects.create(profile=user_profile)
#    player_session.save()

    # Get user's availabilities, or send to availability page
    user_availabilities = Availability.objects.filter(profile=user_profile)
    if not user_availabilities:
        return redirect('availability')
    else:
        sessions = get_suitable_sessions(user_profile)
        if sessions:
            session = sessions[0]
            print(session)
        else:
            session = None
			
	# Testing, don't run the rest
    return redirect('dashboard')
    
	
	# Suitable session?
    if session:
        # Attach a session
        player_session.session = session
        player_session.save()
        user_profile.in_queue = True
        user_profile.save()
    else:
        # Create a session and add the user
        game = Game.objects.get(pk=1)
        session = Session.objects.create(game=game)
        player_session.session = session
        player_session.save()
        user_profile.in_queue = True
        user_profile.save()

    return redirect('dashboard')

# Removes the authenticated player from the queue
@login_required
def exit_queue(request):
    if not request.user.profile.in_queue:
        redirect('dashboard')

	# Get the most recent queue and delete it (as we can have many sessions)
    player_session = Session_Profile.objects.filter(profile=request.user.profile).order_by('-session__start').first()
    player_session.delete()
    request.user.profile.in_queue = False
    request.user.profile.save()
    return redirect('dashboard')

# Get all suitable sessions for a user to join
# Availability existence should be verified prior to this point.
def get_suitable_sessions(profile):
	# Modifiers
	acceptable_mmr_range = 100 # How much above/below us should they be to be viable?
	min_accepted_viability = 0.6 # A value (out of 1) which states how viable a session must be to be included
	# Queueing players details
	user_availabilities = Availability.objects.filter(profile=profile)
	user_connected_accounts = Profile_Connected_Game_Account.objects.filter(profile=profile)
  	
	# Create a list of games to filter based off
	user_accounts = []
	for acc in user_connected_accounts:
		user_accounts.append(acc.game)

	# Testing
	print(user_accounts)
	print(user_availabilities)

	# All the sessions which meet basic requirements (mmr, time/day, playlist, game)
	viable_sessions = []

	# Get any session that matches the availability given (1 hour min.)
	for avail in user_availabilities:
		# The value of the days for filtering by day
		day = -1
		if avail.pref_day == Availability.MONDAY:
			day = 2
		elif avail.pref_day == Availability.TUESDAY:
			day = 3
		elif avail.pref_day == Availability.WEDNESDAY:
			day = 4
		elif avail.pref_day == Availability.THURSDAY:
			day = 5
		elif avail.pref_day == Availability.FRIDAY:
			day = 6
		elif avail.pref_day == Availability.SATURDAY:
			day = 7
		elif avail.pref_day == Availability.SUNDAY:
			day = 1
		print(day)
		# Get any sessions that haven't happened yet, match our day, is one of our games we have set up, and is the right playlist type
		avail_match_sessions = Session.objects.filter(
			start__gte=datetime.datetime.now(),
			game__in=user_accounts, 
			competitive=avail.competitive,
			start__week_day=day,
		).exclude(start__isnull=True)

		# Check the viability of the session
		for session in avail_match_sessions:
			# Get user account connected to this game
			user_acc = Profile_Connected_Game_Account.objects.filter(profile=profile, game=session.game).first()
			# Get the stats of each player that is attached to the session
			player_sessions = Session_Profile.objects.filter(session=session)
			
			# All sessions are suitable until proven otherwise
			suitable = True
			# Check if their MMR is within the range we want
			for player_s in player_sessions:
				prof_acc = Profile_Connected_Game_Account.objects.filter(profile=player_s.profile, game=session.game).first()

				# Cancel if mmr out of range
				if session.competitive:
					if (prof_acc.comp_rank < user_acc.comp_rank - acceptable_mmr_range) or (prof_acc.comp_rank > user_acc.comp_rank + acceptable_mmr_range):
						suitable = False
						break
				else:
					if (prof_acc.cas_rank < user_acc.cas_rank - acceptable_mmr_range) or (prof_acc.cas_rank > user_acc.cas_rank + acceptable_mmr_range):
						suitable = False
						break
			print(suitable)
			# Basic viable session
			if suitable:
				viable_sessions.append(session)

	# Check existence
	if len(viable_sessions) < 1:
		return None
	# Add any sessions that meet viability requirements
	sorted_sessions = []
	for session in viable_sessions:
		v = calc_match_viablity(session)
		if v > min_accepted_viability:
			sorted_sessions.append([v, session])
	
	# Check existence
	if len(sorted_sessions) < 1:
		return None

	# Sort based on viability, highest to lowest
	sorted_sessions.sort(key=lambda v: v[0], reverse=True)

	# Get the best match
	# Exhausted all availabilities and no sessions were matching criteria
	return sorted_sessions[0]

# THE ACTUAL ALGORITHMIC CHECKS
# Calculates how viable a session is for your current profile's weighting
# (commendations create a % viability)
# (sum( (c1*w1)+(c2*w2)+(c3*w3)+(c4*w4) ) / sum( c1 + c2 + c3 + c4 ))
# Where c=commendations, w=weighting
def calc_match_viablity(session):
	weighting_modifiers = [1.0, 0.75, 0.5, 0.25]
	# Dummy data
	return 0.8

def availability(request):
	# Ensure that user is not queued!
	if request.user.profile.in_queue:
		return redirect('dashboard')

	# Remove the reference to an editable availability if it exists.
	if 'avail_url' in request.session:
		del request.session['avail_url']

	avail = retrieve_data('availability', 'profile='+str(request.user.profile.id))
	context = {'title':'Availability', 'Message':'Below is a list of your current availabilities', 'availabilities':avail}

	# Delete data based on the the id provided by the html page
	if(request.GET.get('Remove Availability')):
		delete_availability(request.GET.get('url'))
		return redirect('availability')

	# Redirect to an edit availability page, given the id of the profile to edit
	if(request.GET.get('Edit Availability')):
		request.session['avail_url'] = request.GET.get('url')
		return redirect('edit_availability')

	return render(request, 'mysite/availability.html', context)

# Handles anything that must happen when availability is removed via API
def delete_availability(url):
	delete_data(url)

# Handles new availabilities and editable availabilities
@login_required
def add_availability(request):
	# Ensure that user is not queued!
	if request.user.profile.in_queue:
		return redirect('dashboard')

	context = {
	    'title': 'New Availability',
	    'message' : 'Please enter the details for your new availability.',
	    'editing' : False
	}

	# Creae a new entry, or edit the existing one if it has been given
	if request.method == 'POST':
		form = UserAvailabilityForm(request.POST, user=request.user)

		if form.is_valid():
			instance = form.save(commit=False)
			instance.profile = request.user.profile
			instance.save()

			return redirect('availability')
	else:
		form = UserAvailabilityForm()

	# Set the form to whichever form we are using
	context['form'] = form
	return render(request, 'registration/availability_form.html', context)

# Handles new availabilities and editable availabilities
@login_required
def edit_availability(request):
	# Ensure that user is not queued!
	if request.user.profile.in_queue:
		return redirect('dashboard')

	# Get a potentially editable object from a given url
	if 'avail_url' in request.session:
		url_parts = request.session['avail_url'].split('/')
		# Get the id, which is located at the 6th element in the split list
		id = int(url_parts[5])
		# Get the availability, or send to availability page if it doesnt exist
		try:
			obj = Availability.objects.get(pk=id)
		except model.DoesNotExist:
			return redirect('availability')
		context = {
		    'title': 'Update Availability',
		    'message' : 'Please enter the new details for this availability.'
		}
	# Not editing an entry
	else:
		redirect('add_availability')

	# Creae a new entry, or edit the existing one if it has been given
	if request.method == 'POST':
		form = UserAvailabilityForm(request.POST, instance=obj, user=request.user)

		if form.is_valid():
			instance = form.save(commit=False)
			instance.profile = request.user.profile
			instance.save()

			# Remove the availability url so that the form doesn't default to it
			if 'avail_url' in request.session:
				del request.session['avail_url']

			return redirect('availability')
	# If user just entered page, generate the correct form to display
	else:
		form = UserAvailabilityForm(instance=obj)
	# Set the form to whichever form we are using
	context['form'] = form
	return render(request, 'registration/availability_form.html', context)

# User rating a sessions
@login_required
def rate_session(request):
	context = {
	    'title': 'Rate Session',
	    'message' : 'We hope you\'ve enjoyed your session! Please rate how well it was matched below.',
	}

	# Dummy
	user_session = Session.objects.get(pk=1)
	# Creae a new entry, or edit the existing one if it has been given
	if request.method == 'POST':
		form = RateSessionForm(request.POST, session=user_session, profile=request.user.profile)
		if form.is_valid():
			form.save()
			return redirect('availability')
	else:
		form = RateSessionForm(session=user_session, profile=request.user.profile)

	# Set the form to whichever form we are using
	context['form'] = form
	return render(request, 'registration/availability_form.html', context)
