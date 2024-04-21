from django.db.models import Sum
from django.core.cache import cache
from .models import Short, ShortRating
from shorts import settings
from celery import shared_task
from django.core.mail import send_mail
import random


@shared_task
def editShortRating(short_id):
    try:
        short = Short.objects.only("rating").get(id=short_id)
    except Exception as e:
        print(e)
        return False
    
    shortRating = ShortRating.objects.filter(short_id=short_id).aggregate(rating=Sum("rating"))

    short.rating = shortRating["rating"]
    short.save()
    
    return True


@shared_task
def sendCodeToEmail(email, code):
    # code = str(random.randint(100000, 999999))
    # cache.set(REMOTE_ADDR, (email, code), 60*2, 2)
    
    send_mail(
        "Подтверждение электронной почты",
        f"Ваш код: {code}",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=True,
    )
