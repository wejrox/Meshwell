from django import forms


class FeedbackForm(forms.Form):
  full_name = forms.CharField(max_length=100)
  email = forms.emailField()
  title = forms.CharField(max_length=100)
  message = forms.CharField(widget=forms.Textarea)
