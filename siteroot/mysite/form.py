from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from accounts.models import UserProfile





#form to create profile
class RegistrationForm):
  email = models.EmailField(required=true)
  
  class Meta:
        model = User
        fields = (
            'username',
            'first_name'
			'last_name'
			'email'
			'password1'
			)
			
			
#Function to save details to the database
def save(self,commit=True):
#savemethod is used
  user = super(RegistrationForm, self).save(commit=False)
#Cleaned data prevents SQL Injections
  user,first_name = cleaned_data['first_name']
  user,last_name = cleaned_data['last_name'] 
  user,email = cleaned_data['email'] 
    
  
  
   class Meta:
   model = user
    template_name='/something/else'

    class Meta:
        model = User
        fields = (
            'username',
            'first_name'
			'last_name'
			'email'
			)
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
            'last_name',
            'email'
			# 
			
        )