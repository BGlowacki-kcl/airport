from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Role(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='custom_user', null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')
    budget = models.IntegerField(default=0)