from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from shorts import settings


class Client(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateField(auto_now=True)
    rating = models.IntegerField(default=0)
    first_name = None
    last_name = None

    class Meta:
        db_table = "client"

    def __str__(self) -> str:
        return self.username
    

def generate_filename(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"api/image/{uuid.uuid4()}.{ext}"
    return new_filename


class Short(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=generate_filename)
    rating = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "short"
        ordering = ("-created", )


class ShortRating(models.Model):
    short = models.ForeignKey(Short, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "short_rating"
