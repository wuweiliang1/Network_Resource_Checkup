from django.db import models

# Create your models here.


class Subnet(models.Model):
    subnet = models.CharField(max_length=30)
    description = models.CharField(max_length=500,blank=True)
    type = models.CharField(max_length=10, choices=(('Public', 'Public'), ('Private', 'Private')), default='Public')

    def __str__(self):
        return self.subnet


class SpecialIp(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    description = models.CharField(max_length=500,blank=True)
    belonging_subnet = models.ForeignKey(Subnet, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, choices=(('核心交换机浮动网关', '核心交换机浮动网关'), ('负载均衡设备浮动网关', '负载均衡设备浮动网关'),('核心交换机实网关', '核心交换机实网关'),('负载均衡设备实网关', '负载均衡设备实网关'),('运营商提供网关','运营商提供网关')), default='core_vgw')

    def __str__(self):
        return self.ip + ':' + self.type +' in ' +str(self.belonging_subnet)