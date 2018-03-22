from django.db import models

class Feedback(models.Model):
	name = models.CharField(max_length=120)
	email = models.EmailField()
	title = models.CharField(max_length=254)
	message = models.TextField()
