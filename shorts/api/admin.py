from django.contrib import admin
from . import models


admin.site.register(models.Client)
admin.site.register(models.Short)
admin.site.register(models.ShortRating)
