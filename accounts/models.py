# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    intro = models.TextField(blank=True, null=True, help_text=_("User introduction"))
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    is_dormant = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.username