from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from apps.api.models import Profile, Feedback, Profile_Connected_Game_Account, Availability, Session, Session_Profile
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

	# Get the profile to edit too
	def __init__(self, *args, **kwargs):
		self.profile = kwargs.pop('profile', None)
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self['birth_date'].initial = self.profile.birth_date

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
		user.profile.birth_date = self.cleaned_data['birth_date']
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
	# Add player fields
	def __init__(self, *args, **kwargs):
		self.session = kwargs.pop('session', None)
		super(RateSessionForm, self).__init__(*args, **kwargs)
		# Get all the users connected to the session
		players = Session_Profile.objects.filter(session=self.session)
		for i, player in enumerate(players):
			self.fields['player_%s_id' % i] = forms.CharField(initial=player.profile.id, label='')
			self.fields['player_%s_id' % i].widget = forms.HiddenInput()
			self.fields['player_%s_name' % i] = forms.CharField(disabled=True, label='Player', initial=player.profile.user.username)
			self.fields['player_%s_skill' % i] = forms.BooleanField(label='Skill', required=False)
			self.fields['player_%s_positivity' % i] = forms.BooleanField(label='Positivity', required=False)
			self.fields['player_%s_communication' % i] = forms.BooleanField(label='Communication', required=False)
			self.fields['player_%s_teamwork' % i] = forms.BooleanField(label='Teamwork', required=False)

	def clean(self):
		cleaned_data = super().clean()
		return cleaned_data

	def save(self):
		print("Saving")
