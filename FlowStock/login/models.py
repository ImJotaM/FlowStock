from django.db import models

# Create your models here.
class Usuario():
	name = models.CharField(max_length=100)
	email = models.EmailField(max_length=254, unique=True)
	