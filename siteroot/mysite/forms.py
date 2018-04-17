from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from apps.api.models import Profile, Feedback, Profile_Connected_Game_Account, Availability, Session, Session_Profile
from django.forms import ModelForm

#form to create profile
#RegistrationForm VIEW must be created first as well as URl
class RegistrationForm(UserCreationForm):
	username = forms.CharField(
		max_length=30,
		required = True,
		help_text='Optional.',
		widget=forms.TextInput(attrs={'class':'form-control',}),
	)
	first_name = forms.CharField(
		max_length=30,
		required = False,
		help_text='Optional.',
		widget=forms.TextInput(attrs={'class':'form-control'}),
	)
	last_name = forms.CharField(
		max_length=30,
		required = False,
		help_text='Optional.',
		widget=forms.TextInput(attrs={'class':'form-control'}),
	)
	email = forms.EmailField(
		max_length=254,
		required=True,
		help_text='Required. Enter a valid email address.',
		widget=forms.TextInput(attrs={'class':'form-control', 'type':'text',}),
	)
	birth_date = forms.DateField(
		help_text='Required. Format: YYYY-MM-DD'
	)
	password1 = forms.CharField(
		help_text='Required.',
		required=True,
		max_length=4096,
		widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password',}),
	)
	password2 = forms.CharField(
		help_text='Required.',
		required=True,
		max_length=4096,
		widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password',}),
	)
	#Class meta will dictate what the form uses for its fields
	class Meta:
		model = User
		fields = (
	        	'username',
	        	#'first_name',
			#'last_name',
			#'email',
	        	'birth_date',
		#	'password1',
			#'password2',
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
			user.profile.birth_date = self.cleaned_data['birth_date']
			user.save()
			user.profile.save()

			return user

# User editing profile details
class EditProfileForm(RegistrationForm):
    class Meta:
        model = User
        fields = (
            #'email',
            #'first_name',
            'last_name',
            'birth_date',
        )

# User feedback
class FeedbackForm(forms.ModelForm):
	class Meta:
		model=Feedback
		exclude=[]

# User login
class LoginForm(forms.Form):
	username = forms.CharField(help_text="Enter your username.")
	password = forms.CharField(help_text="Enter your password.", widget=forms.PasswordInput())

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

# When a user can play games
class UserAvailabilityForm(forms.ModelForm):
	pref_day = forms.ChoiceField(
		choices=Availability.PREF_DAY_CHOICES,
		widget=forms.Select(attrs={'class':'form-control'})
	)
	start_time = forms.TimeField(
		required = True,
		help_text= 'Required.',
		widget=forms.TimeInput(attrs={'class':'form-control', 'type':'time'}),
		input_formats=['%H:%M', '%H:%M:%S'],
	)
	end_time = forms.TimeField(
		required = True,
		help_text= 'Required.',
		widget=forms.TimeInput(attrs={'class':'form-control', 'type':'time'}),
		input_formats=['%H:%M', '%H:%M:%S'],
	)
	competitive = forms.BooleanField(
		required = False,
		widget=forms.CheckboxInput(attrs={'class':'form-check-label', 'type':'checkbox'}),
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
				# Check availability existence
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
	# Create fields for rating
	rating = forms.ChoiceField(
		choices=RATINGS,
		widget=forms.RadioSelect(
			attrs={'class':'form-check-input form-check-inline', 'type':'radio'},
		),
	)

	# Run when form is created
	def __init__(self, *args, **kwargs):
		self.session = kwargs.pop('session', None)
		self.profile = kwargs.pop('profile', None)
		super(RateSessionForm, self).__init__(*args, **kwargs)
		# Get our current profile
		# Get all the users connected to the session and add them
		players = Session_Profile.objects.filter(session=self.session).exclude(profile=self.profile.id)
		self.player_count = len(players)
		for i, player in enumerate(players):
			self.fields['player_%s_id' % i] = forms.CharField(initial=player.profile.id, label='')
			self.fields['player_%s_id' % i].widget = forms.HiddenInput()
			self.fields['player_%s_name' % i] = forms.CharField(disabled=True, label='Player', initial=player.profile.user.username)
			self.fields['player_%s_skill' % i] = forms.BooleanField(label='Skill', required=False)
			self.fields['player_%s_positivity' % i] = forms.BooleanField(label='Positivity', required=False)
			self.fields['player_%s_communication' % i] = forms.BooleanField(label='Communication', required=False)
			self.fields['player_%s_teamwork' % i] = forms.BooleanField(label='Teamwork', required=False)
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
			if self.cleaned_data['player_%s_skill' % i]:
				profile.skill_commends += 1
			if self.cleaned_data['player_%s_positivity' % i]:
				profile.positivity_commends += 1
			if self.cleaned_data['player_%s_communication' % i]:
				profile.communication_commends += 1
			if self.cleaned_data['player_%s_teamwork' % i]:
				profile.teamwork_commends += 1
			if self.cleaned_data['player_%s_report' % i]:
				report = Report.objects.create(session=self.session, user_reported=profile, sent_by=self.profile, report_reason='toxic')
				report.save()
			profile.save()











#a
