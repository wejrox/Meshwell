from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


#form to create profile
#RegistrationForm VIEW must be created first as well as URl
class RegistrationForm(UserCreationForm):
  email = models.EmailField(required=true)
  birth_date = models.DateField(null=True, blank=False)
 #Class meta will dictate what the form uses for its fields
  class Meta:
        model = User
        fields = (
            'username',
            'first_name'
			'last_name'
			'email'
            'birth_date'
			'password1'
			)


#Function to save form details
def save(self,commit=True):
#Setting Commit to false,otherwise It will only save the fields existing in UserCreationForm
  user = super(RegistrationForm, self).save(commit=False)
#Adding additional Fields that need to be saved
#Cleaned data prevents SQL Injections
  user.first_name = self.cleaned_data['first_name']
  user.last_name = self.cleaned_data['last_name']
  user.email = self.cleaned_data['email']
  user.birth_date = self.cleaned_data['birth_date']

  if commit:
      user.save()

      return user


 class EditProfileForm(RegistrationForm):


    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'birth_date'
        )


















































































































































































































































            'last_name',
            'email'
			#

        )
