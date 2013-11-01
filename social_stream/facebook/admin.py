from django.contrib import admin

from .models import *


class FacebookPostAdmin(admin.ModelAdmin):
    pass


admin.site.register(FacebookPostAdmin, FacebookPost)
