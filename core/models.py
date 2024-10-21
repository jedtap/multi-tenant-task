from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

import os

class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='tenant_logos/',  blank=True, null=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.email

class Project(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    users = models.ManyToManyField(CustomUser)

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

def validate_file_extension(value):
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.doc', '.docx', '.zip']
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError(f'Unsupported file extension: {ext}')

class Task(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    users = models.ManyToManyField(CustomUser)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True, validators=[validate_file_extension]) 

    def __str__(self):
        return self.title
