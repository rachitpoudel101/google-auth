from django.db import models
from django.contrib.auth.models import User

class CredentialsModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credentials')
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    scope = models.TextField(null=True, blank=True)
    token_type = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Credentials for {self.user.username}"
