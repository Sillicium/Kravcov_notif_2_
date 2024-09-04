from django.contrib import admin

from reminder.models import Reception, ApiKey, Call

admin.site.register(
    [Reception, ApiKey, Call]
)
