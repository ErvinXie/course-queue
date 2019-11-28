from django.contrib import admin

# Register your models here.

from osdqueue.models import user
from osdqueue.models import queue
from osdqueue.models import relation

admin.site.register(user)
admin.site.register(queue)
admin.site.register(relation)
