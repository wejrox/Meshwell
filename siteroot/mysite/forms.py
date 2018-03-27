from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from apps.api.models import Profile, Feedback

#form to create profile
#RegistrationForm VIEW must be created first as well as URl
class RegistrationForm(UserCreationForm):
	first_name = forms.CharField(max_length=30, required = False, help_text='Optional.')
	last_name = forms.CharField(max_length=30, required = False, help_text='Optional.')
	email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
	birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
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
			user.birth_date = self.cleaned_data['birth_date']
			user.save()

			return user

# User editing profile details
class EditProfileForm(RegistrationForm):
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'birth_date',
        )

# User feedback
class FeedbackForm(forms.ModelForm):
	class Meta:
		model=Feedback
		exclude=[]

# User deactivation
class DeactivateUser(forms.Form):
	username = forms.CharField(help_text="Enter your username.")
	password = forms.CharField(help_text="Enter your password.", widget=forms.PasswordInput())
