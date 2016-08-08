from django.db import models
from django.utils import timezone


class Farm(models.Model):
    type = models.CharField(max_length=50)
    display_priority = models.IntegerField(default=100)

    def __str__(self):
        return self.type


class DeviceLayerType(models.Model):
    layer = models.CharField(max_length=50)

    def __str__(self):
        return self.layer


class CactiServer(models.Model):
    name = models.CharField(max_length=20, unique=True)
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    port = models.IntegerField()

    def __str__(self):
        return self.name + '@' + str(self.ip)


class Device(models.Model):
    environment = models.ForeignKey(Farm, on_delete=models.CASCADE)
    layer = models.ForeignKey(DeviceLayerType, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    ip = models.CharField(max_length=20)
    accounting = models.BooleanField(blank=False, default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    cactiServer = models.ForeignKey(CactiServer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Link(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    type = models.CharField(max_length=2, choices=(('EX', 'External'), ('IN', 'Internal')), default='IN')
    accounting = models.BooleanField(blank=False, default=True)
    maximum_speed = models.FloatField(max_length=10)
    created_time = models.DateField(default=timezone.now)
    device = models.ManyToManyField(Device, through='DeviceLinkMember')

    def __str__(self):
        return self.name


class DeviceLinkMember(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    data_source = models.BooleanField(default=False)
    graph_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.data_source:
            return '%s in %s (graphing source)' % (self.link, self.device)
        else:
            return '%s in %s (non graphing source)' % (self.link, self.device)


class TrafficStatsReport(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    stats_interval = models.FloatField(max_length=10)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_time = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(max_length=2000,blank=True,default='无特殊说明')

    def __str__(self):
        return self.name


class TrafficStat(models.Model):
    name = models.CharField(max_length=200, unique=True)
    associated_report = models.ForeignKey(TrafficStatsReport, on_delete=models.CASCADE, null=True)
    data_source = models.ForeignKey(CactiServer, on_delete=models.SET_NULL, null=True)
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null=False)
    type = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    stats_interval = models.IntegerField()
    traffic_sequence = models.CharField(max_length=1000)
    created_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
