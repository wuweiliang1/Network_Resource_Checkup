from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Farm)
admin.site.register(DeviceLayerType)
admin.site.register(CactiServer)
admin.site.register(Device)
admin.site.register(TrafficStatsReport)
admin.site.register(Link)
admin.site.register(DeviceLinkMember)