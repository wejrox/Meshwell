from django import forms
from django.contrib.auth.models import User

class FeedbackForm(forms.Form):
  
  #full_name = forms.CharField(max_length=100)
  #email = forms.emailField()
  
  #used Mihir's forms.py as reference by using class Meta: and model=user
  
  email = models.EmailField(required=true)
  title = forms.CharField(max_length=100)
  message = forms.CharField(widget=forms.Textarea)
  
 #Class meta will dictate what the form uses for its fields
  class Meta:
        model = User
        fields = (
            'first_name'
	    'last_name'
	    'email'
            'title'
            'message'
			)
