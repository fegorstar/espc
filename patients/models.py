from django.db.models import Sum
from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from django.contrib.postgres.fields import ArrayField
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = CloudinaryField(
        'image', folder='espc/profile_pictures', blank=True, null=True)
    state = models.CharField(max_length=250, default="")
    city = models.CharField(max_length=250, default="")
    phone_number = models.CharField(max_length=11)
    nin = models.CharField(max_length=11, blank=True,
                           null=True, verbose_name=_('NIN'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return self.user.email
