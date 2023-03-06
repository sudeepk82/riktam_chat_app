from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

# from djongo import models


# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    admin = models.ForeignKey(
        "AppUser", related_name="created_groups", on_delete=models.CASCADE
    )
    # admin = models.EmbeddedField(
    #     model_container="AppUser",
    #     related_name="created_groups",
    #     on_delete=models.CASCADE,
    # )

    def __str__(self) -> str:
        return self.name


class Message(models.Model):
    msg_text = models.TextField()
    # sender = models.EmbeddedField(
    #     "AppUser", related_name="sent_messages", on_delete=models.CASCADE
    # )
    # group = models.EmbeddedField(
    #     "Group", related_name="messages", on_delete=models.CASCADE
    # )
    sender = models.ForeignKey(
        "AppUser", related_name="sent_messages", on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        "Group", related_name="messages", on_delete=models.CASCADE
    )
    like_users = models.ManyToManyField("AppUser", blank=True)

    def __str__(self) -> str:
        return self.msg_text

class AppUserManager(BaseUserManager):

  def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
    if not email:
        raise ValueError('Users must have an email address')
    email = self.normalize_email(email)
    user = self.model(
        email=email,
        is_staff=is_staff, 
        is_active=True,
        is_superuser=is_superuser, 
        **extra_fields
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password, **extra_fields):
    return self._create_user(email, password, False, False, **extra_fields)

  def create_superuser(self, email, password, **extra_fields):
    user=self._create_user(email, password, True, True, **extra_fields)
    return user

# class AppUser(models.Model):
class AppUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, unique=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    chat_groups = models.ManyToManyField(Group, blank=True)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = AppUserManager()

    class Meta:
        db_table = "app_users"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
