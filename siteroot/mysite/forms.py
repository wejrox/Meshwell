from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from apps.api.models import Profile, Feedback, Profile_Connected_Game_Account, Availability, Session, Session_Profile, Report, Game
from mysite import views
from django.forms import ModelForm
from django.utils.safestring import mark_safe

#form to create profile
#RegistrationForm VIEW must be created first as well as URl
class RegistrationForm(UserCreationForm):
	username = forms.CharField(
		max_length=30,
		required=True,
	)
	first_name = forms.CharField(
		max_length=30,
		required=False,
	)
	last_name = forms.CharField(
		max_length=30,
		required=False,
	)
	email = forms.EmailField(
		max_length=254,
		required=True,
	)
	birth_date = forms.DateField(
		required=True,
		widget=forms.TextInput(attrs={'type':'date'})
	)
	password1 = forms.CharField(
		required=True,
		max_length=4096,
		label='Password',
		widget=forms.PasswordInput(),
	)
	password2 = forms.CharField(
		required=True,
		max_length=4096,
		label='Password (again)',
		widget=forms.PasswordInput(),
	)
	pref_server = forms.ChoiceField(
		choices=Profile.PREF_SERVER_CHOICES,
		widget=forms.Select(),
	)
	tos = forms.BooleanField(
		label=mark_safe('I have read and agree to the <a href="/tos/" target="_blank">Terms of Service</a>')
	)

	#Class meta will dictate what the form uses for its fields
	class Meta:
		model = User
		fields = (
			'username',
			'first_name',
			'last_name',
			'email',
			'birth_date',
			'password1',
			'password2',
		)

	#Function to save form details
	def save(self,commit=True):
		if commit:
			#Setting Commit to false,otherwise It will only save the fields existing in UserCreationForm
			user = super(RegistrationForm, self).save(commit=False)
			#Adding additional Fields that need to be saved
			#Cleaned data prevents SQL Injections
			user.first_name = self.cleaned_data['first_name']
			user.last_name = self.cleaned_data['last_name']
			user.email = self.cleaned_data['email']
			user.save()
			# Get the profile if it's somehow attached, or create one
			profile = user.profile
			if not profile:
				profile = Profile.objects.create(user=user)
			profile.birth_date = self.cleaned_data['birth_date']
			profile.pref_server = self.cleaned_data['pref_server']
			profile.save()

			return user

# User editing profile details
class EditProfileForm(forms.ModelForm):
	username = forms.CharField(
		disabled=True
	)
	birth_date = forms.DateField(
		required=True,
		widget=forms.TextInput(attrs={'type':'date'})
	)
	pref_server = forms.ChoiceField(
		choices=Profile.PREF_SERVER_CHOICES,
		widget=forms.Select(),
	)
	# Get the profile to edit too
	def __init__(self, *args, **kwargs):
		self.profile = kwargs.pop('profile', None)
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self['birth_date'].initial = self.profile.birth_date
		self['pref_server'].initial = [self.profile.pref_server]

	class Meta:
		model = User
		fields = (
			'username',
			'email',
			'first_name',
			'last_name',
		)

	def save(self):
		user = super(EditProfileForm, self).save(commit=False)
		user.save()
		user.profile.birth_date = self.cleaned_data['birth_date']
		user.profile.pref_server = self.cleaned_data['pref_server']
		user.profile.save()
		return user.profile

# User feedback
class FeedbackForm(forms.ModelForm):
	class Meta:
		model=Feedback
		exclude=[]
# User login
class LoginForm(forms.Form):
	username = forms.CharField(help_text="Enter your username.")
	password = forms.CharField(help_text="Enter your password.", widget=forms.PasswordInput())

	def clean(self):
		# Get cleaned data
		cleaned_data = super().clean()
		# Basic data check
		if 'username' in cleaned_data and 'password' in cleaned_data:
			user = authenticate(username=cleaned_data.get('username'), password=cleaned_data.get('password'))
			# User authentication check
			if user is not None:
				# Inactive or banned check
				if not user.is_active:
					raise forms.ValidationError("This account is either banned or deactivated")
				else:
					# Form is all good, process login
					cleaned_data['user'] = user
			else:
				raise forms.ValidationError("Username or password is incorrect")
		else:
			raise forms.ValidationError("Username or password is missing")
		# Return the data
		return cleaned_data

# User deactivation
class DeactivateUser(forms.Form):
	username = forms.CharField(help_text="Enter your username.")
	password = forms.CharField(help_text="Enter your password.", widget=forms.PasswordInput())

# Connect a user account to a game
class ConnectAccountForm(forms.ModelForm):
	class Meta:
		model=Profile_Connected_Game_Account
		fields = (
			'game',
			'game_player_tag',
			'platform',
		)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(ConnectAccountForm, self).__init__(*args, **kwargs)
	
	def save(self):
		print(self.cleaned_data)
		connected_account = Profile_Connected_Game_Account.objects.create(
			profile = self.user.profile,
			platform = self.cleaned_data['platform'],
			game = self.cleaned_data['game'],
			game_player_tag = self.cleaned_data['game_player_tag'],
			cas_rank = self.cleaned_data['cas_rank'],
			comp_rank = self.cleaned_data['comp_rank'],
			)

		connected_account.save()

	def clean(self):
		cleaned_data = super().clean()
		# Make sure account not already connected
		c_acc = cleaned_data.get('game_player_tag')
		game = cleaned_data.get('game')

		# Clean only if account entered
		if c_acc is not None:
			# Account exists already
			p_acc = Profile_Connected_Game_Account.objects.filter(game_player_tag=c_acc).first()
			if p_acc is not None:
				self.add_error('game_player_tag', 'This account is already connected to another user!')
			# Profile already has an account for this game
			if game is not None:
				if Profile_Connected_Game_Account.objects.filter(profile=self.user.profile, game=game).first() is not None:
					self.add_error('game', 'This account already has this game connected.')
			
			# Set the rank if above checks are clear
			if p_acc is None and game is not None:
				ranks = None
				# Get ranks depending on game selected
				if game.name == 'Rainbow Six Siege':
					ranks = views.get_r6siege_ranks(self.user.profile.pref_server, cleaned_data.get('game_player_tag'))
				else:
					raise forms.ValidationError("%s isn't a supported game" % str(game))
				
				# Assign the ranks
				if ranks is not None:
					if 'cas_rank' in ranks and 'comp_rank' in ranks:
						cleaned_data['cas_rank'] = ranks['cas_rank']
						cleaned_data['comp_rank'] = ranks['comp_rank']
					else:
						self.add_error('game_player_tag', 'Ranks not found for this account.')
				else:
					self.add_error('game_player_tag', 'Ranks not found for this account.')
			
		return cleaned_data

# When a user can play games
class UserAvailabilityForm(forms.ModelForm):
	pref_day = forms.ChoiceField(
		choices=Availability.PREF_DAY_CHOICES,
	)
	start_time = forms.TimeField(
		required = True,
		help_text= 'Required.',
		initial='00:00',
		input_formats=['%H:%M', '%H:%M:%S'],
	)
	end_time = forms.TimeField(
		required = True,
		help_text= 'Required.',
		initial='01:00',
		input_formats=['%H:%M', '%H:%M:%S'],
	)
	competitive = forms.BooleanField(
		required = False,
	)
	class Meta:
		model = Availability
		fields = (
			'pref_day',
			'start_time',
			'end_time',
			'competitive',
		)

	# Get the current user for the form to validate against.
	# MUST BE SUPPLIED AS A KWARG.
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(UserAvailabilityForm, self).__init__(*args, **kwargs)
		if 'start_time' in self.initial:
			self.initial['start_time'] = self.initial['start_time'].strftime('%H:%M')
		if 'end_time' in self.initial:
			self.initial['end_time'] = self.initial['end_time'].strftime('%H:%M')

	# Don't allow start time after end time
	def clean(self):
		# Get cleaned data
		cleaned_data = super().clean()
		start_time = cleaned_data.get('start_time')
		end_time = cleaned_data.get('end_time')

		# Additional validation
		if start_time and end_time:
			# Check start and end time for overlap
			if start_time >= end_time:
				self.add_error('start_time', forms.ValidationError("You cannot start after/when you finish!"))
				#raise forms.ValidationError("You cannot start after you finish!")
			# If the start time is overlapping, it is removed from cleaned data.
			# This else ensures that we only continue with checks if the times are valid.
			else:
				# In case we're editing
				if self.instance is not None:
					avail_pk = self.instance.pk
				else:
					avail_pk = -1
				# Check availability already existing
				avail_start = Availability.objects.filter(
					profile=self.user.profile,
					start_time__range=(
						cleaned_data.get('start_time'),
						cleaned_data.get('end_time'),
					),
					pref_day=cleaned_data.get('pref_day'),
				).exclude(pk=avail_pk)

				avail_end = Availability.objects.filter(
					profile=self.user.profile,
					end_time__range=(
						cleaned_data.get('start_time'),
						cleaned_data.get('end_time'),
					),
					pref_day=cleaned_data.get('pref_day'),
				).exclude(pk=avail_pk)

				avail_inside = Availability.objects.filter(
					profile=self.user.profile,
					start_time__lte=cleaned_data.get('start_time'),
					end_time__gte=cleaned_data.get('end_time'),
					pref_day=cleaned_data.get('pref_day'),
				).exclude(pk=avail_pk)

				# Error if overlap occurs
				if any ([avail_start, avail_inside, avail_end]):
					raise forms.ValidationError("An availability already exists for this time and day, or you are overlapping.")
		# Always return the cleaned data!
		return cleaned_data

class RateSessionForm(forms.Form):
	# A tuple for rating numbers user can give
	RATINGS=((0, '0'),(1, '1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'))
	COMMENDS=Profile.COMMENDS_CHOICES
	# Create fields for rating
	rating = forms.ChoiceField(
		choices=RATINGS,
		widget=forms.RadioSelect(
#			# DOES NOT GET APPLIED FOR SOME REASON
#			attrs={'class':'form-check-inline'}
		),
		initial=[2]
	)

	# Run when form is created
	def __init__(self, *args, **kwargs):
		self.session = kwargs.pop('session', None)
		self.profile = kwargs.pop('profile', None)
		super(RateSessionForm, self).__init__(*args, **kwargs)
		# Get all the users connected to the session and add them
		players = Session_Profile.objects.filter(session=self.session).exclude(profile=self.profile.id)
		self.player_count = len(players)
		for i, player in enumerate(players):
#            # Get teammates ign so the user knows who they are (DISABLED RIGHT NOW AS WE ARE TESTING AND NO ACCOUNT EXISTS)
#            ign = Profile_Connected_Game_Account.filter(game=self.session.game.id, profile=player.profile.id).first()
			self.fields['player_%s_id' % i] = forms.CharField(initial=player.profile.id, label='')
			self.fields['player_%s_id' % i].widget = forms.HiddenInput()
			self.fields['player_%s_name' % i] = forms.CharField(disabled=True, label='Player', initial=player.profile.user.username)
			self.fields['player_%s_commends' % i] = forms.MultipleChoiceField(
				label='Commendations', 
				required=False,
				choices=self.COMMENDS, 
			)
			self.fields['player_%s_commends' % i].widget = forms.CheckboxSelectMultiple (attrs={'class':'form-check-inline'})
			self.fields['player_%s_report' % i] = forms.BooleanField(label='Report', required=False)

	def clean(self):
		cleaned_data = super().clean()
		# Custom cleaning

		return cleaned_data

	def save(self):
		# Get their session Details
		session_profile = Session_Profile.objects.filter(profile=self.profile, session=self.session).first()
		# Save rating
		session_profile.rating = self.cleaned_data.get('rating')
		session_profile.save()

		# Apply commendations and reports
		for i in range(0, self.player_count):
			# Get profile
			profile = Profile.objects.get(pk=self.cleaned_data['player_%s_id' % i])
			# Apply commendations and reports
			if self.cleaned_data['player_%s_commends' % i]['skill']:
				profile.skill_commends += 1
			if self.cleaned_data['player_%s_commends' % i]['sportsmanship']:
				profile.sportsmanship_commends += 1
			if self.cleaned_data['player_%s_commends' % i]['communication']:
				profile.communication_commends += 1
			if self.cleaned_data['player_%s_commends' % i]['teamwork']:
				profile.teamwork_commends += 1
			if self.cleaned_data['player_%s_report' % i]:
				report = Report.objects.create(session=self.session, user_reported=profile, sent_by=self.profile, report_reason='toxic')
				report.save()
			profile.received_ratings += 1
			profile.save()

class SelectMatchmakingOptionsForm(forms.Form):
	'''
	Form displayed as modal on dashboard
	'''
	commend_priority_1 = forms.ChoiceField(
		choices=Profile.COMMENDS_CHOICES,
	)
	commend_priority_2 = forms.ChoiceField(
		choices=Profile.COMMENDS_CHOICES,
	)
	commend_priority_3 = forms.ChoiceField(
		choices=Profile.COMMENDS_CHOICES,
	)
	commend_priority_4 = forms.ChoiceField(
		choices=Profile.COMMENDS_CHOICES,
	)

	# Should the matchmaking ignore commends etc.?
	ignore_matchmaking = forms.BooleanField(required=False)
	# Should we search for competitive sessions? 
	# CURRENTLY DISABLED, COMPETITIVE PREF IS SET ON AVAILABILITIES
	# competitive = forms.BooleanField()

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(SelectMatchmakingOptionsForm, self).__init__(*args, **kwargs)
		# Get the weighting details of current profile
		self.fields['commend_priority_1'].initial = self.user.profile.commend_priority_1
		self.fields['commend_priority_2'].initial = self.user.profile.commend_priority_2
		self.fields['commend_priority_3'].initial = self.user.profile.commend_priority_3
		self.fields['commend_priority_4'].initial = self.user.profile.commend_priority_4
		# Get preferred game
		games_a = Profile_Connected_Game_Account.objects.filter(profile=self.user.profile)
		self.fields['pref_game'] = forms.ChoiceField(choices=[(g.game.id, g.game.name) for g in games_a])
		if self.user.profile.pref_game is not None:
			self.fields['pref_game'].initial = self.user.profile.pref_game.name
		elif len(games_a) > 0:
			self.fields['pref_game'].initial = games_a[0].game.name
		# Set matchmaking override
		self.fields['ignore_matchmaking'].initial = self.user.profile.ignore_matchmaking

	def save(self):
		# Save user commend priorities
		self.user.profile.commend_priority_1 = self.cleaned_data.get('commend_priority_1')
		self.user.profile.commend_priority_2 = self.cleaned_data.get('commend_priority_2')
		self.user.profile.commend_priority_3 = self.cleaned_data.get('commend_priority_3')
		self.user.profile.commend_priority_4 = self.cleaned_data.get('commend_priority_4')
		# Save override status
		self.user.profile.ignore_matchmaking = self.cleaned_data.get('ignore_matchmaking')
		# Save preferred game
		self.user.profile.pref_game = Game.objects.get(id=self.cleaned_data.get('pref_game'))
		# Save changes made
		self.user.profile.save()

	def clean(self):
		cleaned_data = super().clean()
		# Make sure no priorities occur more than once
		if 	(cleaned_data['commend_priority_1'] == cleaned_data['commend_priority_2'] or
			cleaned_data['commend_priority_1'] == cleaned_data['commend_priority_3'] or
			cleaned_data['commend_priority_1'] == cleaned_data['commend_priority_4']):
			self.add_error('commend_priority_1', 'You cannot have duplicate priorities.')
		if 	(cleaned_data['commend_priority_2'] == cleaned_data['commend_priority_3'] or
			cleaned_data['commend_priority_2'] == cleaned_data['commend_priority_4']):
			self.add_error('commend_priority_2', 'You cannot have duplicate priorities.')
		if 	(cleaned_data['commend_priority_3'] == cleaned_data['commend_priority_4']):
			self.add_error('commend_priority_3', 'You cannot have duplicate priorities.')
