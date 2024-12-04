from django.db import models # type: ignore
from django.contrib.auth import *
from django.contrib.auth.models import User 
# Create your models here.
class Document(models.Model):
    docname = models.CharField(max_length=200)   
    authors = models.ManyToManyField(User, related_name="documents")
    uploadTime = models.DateTimeField(auto_now_add=True)