from django.contrib import admin
from . import models

admin.site.register(models.ChatThread)
admin.site.register(models.Message)
