from apps.api.models import Profile, Profile_Connected_Game_Account, Availability, Session, Session_Profile, Game
from rest_framework import viewsets
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
import requests, requests.auth, json, urllib.parse, datetime, math
from mysite.forms import FeedbackForm, DeactivateUser, RegistrationForm, EditProfileForm, ConnectAccountForm, UserAvailabilityForm, RateSessionForm, LoginForm, SelectMatchmakingOptionsForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import login as contrib_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.signals import request_finished
from django.dispatch import receiver
from django.urls import reverse, resolve
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Import settings
from django.conf import settings
#from mysite import private_settings

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
def dashboard(request):
	'''
	Displays the dashboard hub to the user.
	Final context layout can be accessed via:
	(where id = the unique identifier of that entry. Use loops on that aspect to loop through the entries.)
	title
	message
	profile.<username/first_name/last_name/pref_server/birth_date/sessions_played/teamwork_commends/sportsmanship_commends/skill_commends/communcation_commends/discord_id>
	connected_accounts.*
	availabilities.*
	prev_sessions.{id}.session_profile_id
	prev_sessions.{id}.game.<icon/name>
	prev_sessions.{id}.session.<start/end_time/viability/rating>
	prev_sessions.{id}.players.{id}.<name/teamwork_commends/sportsmanship_commends/skill_commends/communication_commends>
	queue.session.<game_name, start, end_time, viability>
	'''
	context = {
		'title':'Dashboard',
		'message':'Play Together. Mesh Well.',

		#Profile Context Items
		'profile': {
			'username':request.user.username,
			'first_name':request.user.first_name,
			'last_name':request.user.last_name,
			'pref_server':request.user.profile.pref_server,
			'birth_date':request.user.profile.birth_date,
			'sessions_played':request.user.profile.sessions_played,
			'teamwork_commends':request.user.profile.teamwork_commends,
			'sportsmanship_commends':request.user.profile.sportsmanship_commends,
			'skill_commends':request.user.profile.skill_commends,
			'communication_commends':request.user.profile.communication_commends,
			'discord_id':request.user.profile.discord_id,
		}
	}

	context['connected_accounts'] = Profile_Connected_Game_Account.objects.filter(profile=request.user.profile)
	context['availabilities'] = Availability.objects.filter(profile=request.user.profile)
	# Get all required data for displaying previous sessions
	usr_ses_prof = Session_Profile.objects.filter(profile=request.user.profile, session__start__lt=timezone.now()).exclude(session__end_time__isnull=True).order_by('-session__start')
	sessions = Session.objects.filter(pk__in=usr_ses_prof.values_list('session__id', flat=True))
	context['prev_sessions'] = {}
	i = 0
	# Get what is to be displayed from each session
	for session in sessions:
		# Find the session profiles, viability, game details
		session_profiles = Session_Profile.objects.filter(session=session)
		user_session_profile = session_profiles.filter(profile=request.user.profile)
		session_viability = math.floor(calc_match_viablity(request.user.profile, session) * 100)
		game_icon = session.game.image.url
		game_name = session.game.name
		start_time = session.start
		context['prev_sessions'][str(i)] = {
			'game':{
				'icon':session.game.image.url,
				'name':session.game.name,
			},
			'session':{
				'id':session.id,
				'start':session.start,
				'end_time':session.end_time,
				'viability':session_viability,
				'rating':user_session_profile[0].rating,
			},
			'session_profile_id':user_session_profile[0].id,
		}

		count = 0
		context['prev_sessions'][str(i)]['players'] = {}
		# Assign each player to this session
		for ses_p in session_profiles:
			# Get their attached account
			game_account = Profile_Connected_Game_Account.objects.filter(game=session.game, profile=ses_p.profile).first()
			if game_account is None:
				break
			# Initialise the player storage
			context['prev_sessions'][str(i)]['players'][str(count)] = {}
			# Assign details
			context['prev_sessions'][str(i)]['players'][str(count)]['name'] = game_account.game_player_tag
			context['prev_sessions'][str(i)]['players'][str(count)]['teamwork_commends'] = ses_p.profile.teamwork_commends
			context['prev_sessions'][str(i)]['players'][str(count)]['sportsmanship_commends'] = ses_p.profile.sportsmanship_commends
			context['prev_sessions'][str(i)]['players'][str(count)]['skill_commends'] = ses_p.profile.skill_commends
			context['prev_sessions'][str(i)]['players'][str(count)]['communication_commends'] = ses_p.profile.communication_commends

			# Go to next connnected user
			count += 1
		# Go to next session
		i += 1

	# Get the current queue's session if it exists
	if request.user.profile.in_queue:
		p_ses = Session_Profile.objects.filter(profile=request.user.profile, session__start__gt=datetime.datetime.now()).first()
		context['queue'] = {}
		if p_ses is not None and p_ses.session is not None:
			context['queue']['session'] = {
				'game_name':p_ses.session.game.name,
				'start':p_ses.session.start,
				'end_time':p_ses.session.end_time,
				'viability':str(math.floor(calc_match_viablity(request.user.profile, p_ses.session) * 10000) / 100) + " %"
			}
		# Can't do timer yet, since it isn't in the model. Can add in next week.
		#context['queue']['start'] = p_ses.datetime_created

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

# About us
def about_us(request):
	context = {
		'title':'About Us',
		'message':'The About Us page for Meshwell.',
	}
	return render(request, 'mysite/about_us.html', context)

# Terms of Service
def terms_of_service(request):
	context = {
		'title':'Terms of Service',
		'message':'Terms of service page for Meshwell.',
	}
	return render(request, 'mysite/terms_of_service.html', context)

# Privacy Policy
def privacy_policy(request):
	context = {
		'title':'Privacy Policy',
		'message':'The privacy policy for Meshwell.',
	}
	return render(request, 'mysite/privacy_policy.html', context)

# Catalog of games
def catalog(request):
	context = {
		'title':'Games Catalog',
		'message':'This is a stub page for our games catalog. No functionality has been added yet.',
	}
	return render(request, 'mysite/catalog.html', context)

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
	data = dict()
	context = {'title':'Edit Profile'}
	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user, profile=request.user.profile)

		if form.is_valid():
			data['form_is_valid'] = True
			form.save()
		else:
			data['form_is_valid'] = False
	else:
		form = EditProfileForm(instance=request.user, profile=request.user.profile)

	context['form'] = form
	data['html_form'] = render_to_string('mysite/edit_profile.html',
										context,
										request=request
										)
	return JsonResponse(data)

# Login. Implemented here to prevent logged in users from accessing the page
def a_login(request):
	data = dict()
	data['user_inactive'] = False
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			data['form_is_valid'] = True
			user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
			login(request, user)
		else:
			data['form_is_valid'] = False
	else:
		form = LoginForm()

	context = {'form': form}
	data['html_form'] = render_to_string('registration/login.html',
										context,
										request=request
										)
	return JsonResponse(data)

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
	context = {
		'title':'Connect Game Account',
	}
	data = dict()
	if request.method == 'POST':
		form = ConnectAccountForm(request.POST, user=request.user)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
		else:
			data['form_is_valid'] = False
	else:
		form = ConnectAccountForm(user=request.user)

	# Set the form to whichever form we are using
	context['form'] = form
	data['html_form'] = render_to_string('account/connect_account.html',
										context,
										request=request
										)
	return JsonResponse(data)

@login_required
def remove_connected_account(request, pk):
	acc = Profile_Connected_Game_Account.objects.filter(pk=pk).first()
	if acc:
		if acc.profile == request.user.profile:
			acc.delete()
	return redirect('dashboard')

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
def get_r6siege_ranks(pref_server, player_tag):
	url = 'https://r6db.com/api/v2/players?name=' + player_tag
	headers = { 'X-App-Id':'MyRequest' }
	response = requests.get(url, headers=headers)

	# Try get the ranks or cancel if we can't
	try:
		data = response.json()
	except:
		return None

	# Cancel the check if the user was not found or too many were found
	if not response.ok or len(data) != 1:
		return None

	# Decide which region to check
	region = pref_server
	if region == 'Oceania' or region == 'Asia' or region == 'Middle-East':
		region = 'apac'
	elif region == 'South America' or region == 'US-West' or region == 'US-East':
		region = 'ncsa'
	elif region == 'Europe' or region == 'South Africa':
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
	player_session = Session_Profile.objects.create(profile=user_profile)
	player_session.save()

	# Get user's availabilities, or send to availability page
	user_availabilities = Availability.objects.filter(profile=user_profile)
	if not user_availabilities:
		return redirect('availability')
	else:
		sessions = get_suitable_sessions(user_profile)
		if sessions:
			session = sessions[0] # The session and availability
		else:
			session = None

	# Testing, don't run the rest
#	return redirect('dashboard')

	# Suitable session?
	if session:
		join_session(player_session, session[1][0], session[1][1])
	### REPLACE WITH A REDIRECTION TO A SESSION CREATION FORM! ###
	else:
		# Create a session and add the user
		player_acc = Profile_Connected_Game_Account.objects.filter(profile=user_profile).first()
		game = Game.objects.get(id=player_acc.game.id)
		session = Session.objects.create(game=game)
		session.start = timezone.now()
		session.save()
		player_session.session = session
		player_session.save()
		user_profile.in_queue = True
		user_profile.save()

	return redirect('dashboard')

def join_session(session_profile, session, avail):
	'''
	Adds a user to a given session, overwriting the time of the session if necessary.
	Returns True on success, False on failure
	'''

	# Ensure space available
	if not session.space_available:
		return False

	# Attach the session
	session_profile.session = session
	session_profile.profile.in_queue = True

	# Set the session begin and end time to where it intersected
	if avail.start_time > session.start.time():
		session.start.time = avail.start_time
	if avail.end_time < session.end_time:
		session.end_time = avail.end_time

	# Set session remaining spaces
	connected_players = Session_Profile.objects.filter(session=session)
	if len(connected_players) >= session.game.max_players:
		session.space_available = False

	# Save database
	session_profile.profile.save()
	session_profile.save()
	session.save()

	return True

# Removes the authenticated player from the queue
@login_required
def exit_queue(request):
	if not request.user.profile.in_queue:
		redirect('dashboard')

	# Get the most recent queue (since we could have played before)
	player_session = Session_Profile.objects.filter(profile=request.user.profile).order_by('-session__start').first()
	# Session now has spaces (regardless of if there were spaces before)
	player_session.session.space_available = True
	player_session.session.save()
	# Delete session if nobody is in it
	sessions = Session_Profile.objects.filter(session=player_session.session)
	if sessions is None:
		Session_Profile.objects.delete(player_session.session)
	# Remove our player session
	player_session.delete()
	request.user.profile.in_queue = False
	request.user.profile.save()
	return redirect('dashboard')

# Get all suitable sessions for a user to join
# Availability existence should be verified prior to this point.
def get_suitable_sessions(profile):
	'''
	Gets all suitable sessions for a user, above the minimum amount specified.
	Returns the sessions as a list of 2 elements [viability, [session, availability]]
	'''
	# Modifiers
	acceptable_mmr_range = 100 # How much above/below us should they be to be viable?
	min_accepted_viability = 0.4 # A value (out of 1) which states how viable a session must be to be included
	# Queueing players details
	user_availabilities = Availability.objects.filter(profile=profile)
	user_connected_accounts = Profile_Connected_Game_Account.objects.filter(profile=profile)

	# Create a list of games to filter based off
	user_accounts = []
	for acc in user_connected_accounts:
		user_accounts.append(acc.game)

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

		# Get any sessions that haven't happened yet, match our day, is one of our games we have set up, is the right playlist type, and has spaces available
		avail_match_sessions = Session.objects.filter(
			start__gte=datetime.datetime.now(),
			game__in=user_accounts,
			competitive=avail.competitive,
			start__week_day=day,
			space_available=True,
		).exclude(start__isnull=True)

		# Check the viability of the session
		for session in avail_match_sessions:
			# Only check them if user availability time overlaps by an hour at least
			if is_time_acceptable(session, avail):
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
				# Basic viable session
				if suitable:
					viable_sessions.append([session, avail])

	# Check existence
	if len(viable_sessions) < 1:
		return None
	# Add any sessions that meet viability requirements
	sorted_sessions = []
	for session in viable_sessions:
		v = calc_match_viablity(profile, session[0])
		if v > min_accepted_viability:
			sorted_sessions.append([v, session])

	# Check existence
	if len(sorted_sessions) < 1:
		return None

	# Sort based on viability, highest to lowest
	sorted_sessions.sort(key=lambda v: v[0], reverse=True)

	# Get the best match
	# Exhausted all availabilities and no sessions were matching criteria
	return sorted_sessions

# THE ACTUAL ALGORITHMIC CHECKS
# Calculates how viable a session is for your current profile's weighting
# (commendations create a % viability)
# sum(each_player:(c1/tsp*w1)+(c2/tsp*w2)+(c3/tsp*w3)+(c4/tsp*w4)) / pc
# Where c=commendations, , tsp=total sessions played, w=weighting, pc=Player Count
def calc_match_viablity(user_profile, session):
	# What each should be worth out of 1 (Team, Comm, Skill, Sport)
	weight = [ 0.5, 0.25, 0.125, 0.125 ]
	# Assign weights to commends by checking if their names are the same
	modifiers = { 'Teamwork':1.0, 'Communication':1.0, 'Skill':1.0, 'Sportsmanship':1.0, }
	for key, value in modifiers.items():
		if user_profile.commend_priority_1 == key:
			modifiers[key] = weight[0]
		elif user_profile.commend_priority_2 == key:
			modifiers[key] = weight[1]
		elif user_profile.commend_priority_3 == key:
			modifiers[key] = weight[2]
		elif user_profile.commend_priority_4 == key:
			modifiers[key] = weight[3]

	# Players connected to the session
	players = Session_Profile.objects.filter(session=session)
	players = players.exclude(profile=user_profile)
	# How much the sessions commends are worth after they have been weighted
	weighted_commends = { 'Teamwork':0.0, 'Communication':0.0, 'Skill':0.0, 'Sportsmanship':0.0, }
	total_commends = { 'Teamwork':0, 'Communication':0, 'Skill':0, 'Sportsmanship':0, }
	player_viability = {}
	# Weigh their commendations based on what the user believes is important
	for player in players:
		num_sess = player.profile.received_ratings

		# If they've played a session, grade them.
		if num_sess > 0:
			teamwork = (player.profile.teamwork_commends / num_sess) * modifiers['Teamwork']
			communication = (player.profile.communication_commends / num_sess) * modifiers['Communication']
			skill = (player.profile.skill_commends / num_sess) * modifiers['Skill']
			sportsmanship = (player.profile.sportsmanship_commends / num_sess) * modifiers['Sportsmanship']

			player_viability[player.id] = teamwork + communication + skill + sportsmanship
		# If not, we just give them 0.5
		else:
			player_viability[player.id] = 0.5

	# Calculate the sum of the viability of all players
	total_viability = 0.0
	for key in player_viability:
		total_viability += player_viability[key]

	# Get the average viability to return as our viability percentage
	if len(players) > 0:
		averaged_viability = total_viability / len(players)
	else:
		averaged_viability = 0.5

	return averaged_viability

# Checks if the time is at least an hour inside availability
# Returns True if so, else False
def is_time_acceptable(session, availability):
	min_end = session.start + datetime.timedelta(hours=1)
	# Check if the session exists within our availability
	if session.start.time() >= availability.start_time and min_end.time() <= availability.end_time:
		return True
	# Check if the session is before our start time but goes at least an hour into our availability
	if session.start.time() <= availability.start_time and min_end.time() <= availability.end_time:
		return True

	# To reach here, the session isn't within our availability and it doesn't overlap
	return False

# Handles anything that must happen when availability is removed via API
@login_required
def remove_availability(request, pk):
	avail = Availability.objects.filter(pk=pk).first()
	if avail:
		if avail.profile == request.user.profile:
			avail.delete()
	return redirect('dashboard')

# Handles new availabilities and editable availabilities
@login_required
def add_availability(request):
	# Ensure that user is not queued!
	if request.user.profile.in_queue:
		return redirect('dashboard')

	data = dict()

	context = {
		'title': 'Add Availability',
		'message' : 'Please enter the details for your new availability.',
	}
	# Creae a new entry, or edit the existing one if it has been given
	if request.method == 'POST':
		form = UserAvailabilityForm(request.POST, user=request.user)

		if form.is_valid():
			instance = form.save(commit=False)
			instance.profile = request.user.profile
			instance.save()
			data['form_is_valid'] = True
		else:
			data['form_is_valid'] = False
	else:
		form = UserAvailabilityForm()

	# Set the form to whichever form we are using
	context['form'] = form
	data['html_form'] = render_to_string('account/add_availability.html',
									context,
									request=request
									)
	return JsonResponse(data)

# Handles new availabilities and editable availabilities
@login_required
def edit_availability(request, pk):
	# Ensure that user is not queued!
	if request.user.profile.in_queue:
		return redirect('dashboard')
	data = dict()

	context = {
		'title': 'Edit Availability',
		'message' : 'Please enter the new details for your availability.',
	}
	# Ensure availability exists to edit
	avail = Availability.objects.filter(pk=pk).first()
	if avail is None:
		raise PermissionDenied

	# Creae a new entry, or edit the existing one if it has been given
	if request.method == 'POST':
		form = UserAvailabilityForm(request.POST, instance=avail, user=request.user)

		if form.is_valid():
			instance = form.save(commit=False)
			instance.profile = request.user.profile
			instance.save()
			data['form_is_valid'] = True

		else:
			data['form_is_valid'] = False
	# If user not tried to post, give them the form
	else:
		form = UserAvailabilityForm(instance=avail)
	# Set the form to whichever form we are using
	context['form'] = form
	data['html_form'] = render_to_string('account/edit_availability.html',
										context,
										request=request
										)
	return JsonResponse(data)

# User rating a sessions
@login_required
def rate_session(request, pk):
	context = {
		'title': 'Rate Session',
		'message' : 'We hope you\'ve enjoyed your session! Please rate how well it was matched below.',
	}
	data = dict()

	# Get the session we would rate
	session = Session.objects.filter(pk=pk).first()
	# Redirect to dashboard if the user has already rated this session
	if session is not None:
		session_profile = Session_Profile.objects.filter(session__pk=pk, profile=request.user.profile).first()
		if session_profile:
			if session_profile.rating is not None:
				data['already_rated'] = True
	else:
		data['doesnt_exist'] = True

	# Don't try to make a form if the session doesn't exist or has already been rated
	if 'doesnt_exist' in data or 'already_rated' in data:
		raise PermissionDenied

	# Attempt to rate if data 'post'ed, or return the form
	if request.method == 'POST':
		form = RateSessionForm(request.POST, session=session, profile=request.user.profile)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
		else:
			data['form_is_valid'] = False
	else:
		form = RateSessionForm(session=session, profile=request.user.profile)

	# Set the form to whichever form we are using
	context['form'] = form
	data['html_form'] = render_to_string('mysite/rate_session.html',
										context,
										request=request
										)
	return JsonResponse(data)

@login_required
def discord_disconnect_account(request):
	'''
	Removes the reference to the user id from the profile that is currently logged in
	'''
	request.user.profile.discord_id = None
	request.user,profile.save()
	return redirect('dashboard')

@login_required
def discord_callback(request):
	'''
	When a user authenticates via discord, this is where discord sends them.
	discord gives a 'user' object but we only take the snowflake (user id) as its all we need.
	Steps are: Get user permission (token), get user details (using token as authentication),
	store id, add user to server (using bot token in header and user token in json)
	'''
	error = request.GET.get('error', '')
	if error:
		print(error)
		# NEED TO IMPLEMENT ERROR
		return redirect('dashboard')

	code = request.GET.get('code')
	if code is None:
		return redirect('dashboard')
	access_token = discord_get_access_token(code)
	id = discord_get_user_id(access_token)

	# Check if id get was a failure
	if id == -1:
		return redirect('dashboard')

	# Add them to the server
	server_add_success = discord_put_user_on_server(access_token, id)

	if server_add_success:
		print("Added user %s to server" % id)
		# Set the current users discord_id
		request.user.profile.discord_id = id
		request.user.profile.save()

	return redirect('dashboard')

def discord_get_access_token(code):
	'''
	Gets an authenticated access token from the callback request
	'''
	client_auth = requests.auth.HTTPBasicAuth(private_settings.CLIENT_ID, private_settings.CLIENT_SECRET)
	data = {
				"client_id": private_settings.CLIENT_ID,
				"client_secret": private_settings.CLIENT_SECRET,
				"grant_type": "authorization_code",
				"code": code,
				"redirect_uri": private_settings.REDIRECT_URI,
	}
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}
	response = requests.post(
				"https://discordapp.com/api/oauth2/token",
				data,
				headers,
				)
	token_json = response.json()
	return token_json['access_token']

def discord_get_user_id(access_token):
	'''
	Returns a user id (snowflake)
	Uses a users access token to get user details
	'''
	headers = {'Authorization': 'Bearer ' + access_token}
	response = requests.get('https://discordapp.com/api/users/@me', headers=headers)
	user_json = response.json()

	# Request failed
	if response.status_code >= 300:
		return -1

	id = user_json['id']
	return id

def discord_put_user_on_server(access_token, discord_id):
	'''
	Adds the user that authenticated into the server automatically
	'''
	headers = {'Authorization': 'Bot ' + private_settings.BOT_TOKEN, 'Content-Type':'application/json'}
	data = {'access_token': '' + access_token}
	response = requests.put('https://discordapp.com/api/guilds/'+private_settings.GUILD_ID+'/members/'+discord_id, headers=headers, json={'access_token':str(access_token)})

	if response.status_code >= 300:
		return False
	return True

def manual_matchmaking(request):
	'''
	User selects from a list of current sessions, given the viability
	'''
	context = {'title':'Manual Matchmaking'}
	context['sessions'] = {}
	sessions = get_suitable_sessions(request.user.profile)
	i = 0
	if sessions is not None:
		for sv in sessions:
			context['sessions'][str(i)] = {}
			context['sessions'][str(i)]['session'] = {}
			context['sessions'][str(i)]['session']['id'] = sv[1][0].id
			# Get the percentage to 2 decimal places
			context['sessions'][str(i)]['session']['viability'] = str(math.floor(sv[0] * 10000) / 100) + " %"
			context['sessions'][str(i)]['session']['start'] = sv[1][0].start
			context['sessions'][str(i)]['session']['end_time'] = sv[1][0].end_time
			context['sessions'][str(i)]['session']['competitive'] = sv[1][0].competitive
			context['sessions'][str(i)]['game_image'] = sv[1][0].game.image.url

	if request.GET.get('Join Session'):
		session_id = request.GET.get('id')
		session = sessions[int(session_id)][1][0]
		avail = sessions[int(session_id)][1][1]
		# Create a user session
		player_session = Session_Profile.objects.create(profile=request.user.profile)
		player_session.save()

		join_session(player_session, session, avail)
		return redirect('edit_availability')
	return render(request, 'mysite/manual_matchmaking_list.html', context)

@login_required
def matchmaking_preferences(request):
	'''
	Modal for setting matchmaking preferences
	'''
	context = {
		'title': 'Preferences',
	}
	data = dict()

	# Attempt to rate if data 'post'ed, or return the form
	if request.method == 'POST':
		form = SelectMatchmakingOptionsForm(request.POST, user=request.user)
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
		else:
			data['form_is_valid'] = False
	else:
		form = SelectMatchmakingOptionsForm(user=request.user)

	# Set the form to whichever form we are using
	context['form'] = form
	data['html_form'] = render_to_string('account/matchmaking_preferences.html',
										context,
										request=request
										)
	return JsonResponse(data)
