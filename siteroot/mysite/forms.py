from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from apps.api.models import Profile, Feedback, User_Preference, Profile_Connected_Game_Account, Availability
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
		start_time = forms.TimeField(
			required = True,
			help_text= 'Required.',
			widget=forms.TimeInput(attrs={'class':'form-control', 'type':'time'}),
			input_formats=['%H:%M'],
		)
		end_time = forms.TimeField(
			required = True,
			help_text= 'Required.',
			widget=forms.TimeInput(attrs={'class':'form-control', 'type':'time'}),
			input_formats=['%H:%M'],
		)
		competitive = forms.BooleanField(
			required = False,
			widget=forms.CheckboxInput(attrs={'class':'form-check', 'type':'checkbox'}),
		)
		class Meta:
				model = Availability
				fields = (
				'pref_day',
				'start_time',
				'end_time',
				'competitive',
				)

class EditAvailabilityForm(forms.ModelForm):
        class Meta:
                model = Availability
                fields = (
                'pref_day',
                'start_time',
                'end_time',
                'competitive',
                )
