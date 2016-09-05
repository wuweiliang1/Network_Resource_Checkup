from django.shortcuts import render
from django.views import generic
from .models import *
import ipaddress
from django.http import HttpResponse
# Create your views here.


class IndexView(generic.ListView):
    template_name = 'Ip_Mgmt/query.html'

    def get_queryset(self):
        return Subnet.objects.order_by('id')


def query_via_ip(request):
    if request.method == 'GET':
        try:
            ip = ipaddress.ip_address(request.GET['query_ip'])
        except ValueError:
            return HttpResponse('你查询的不是一个有效的IP地址！')
        if ip.version != 4:
            return HttpResponse('别蒙我，我们公司哪里来的IPv6地址？')
        subnets = Subnet.objects.all()
        return_txt = request.GET['query_ip'] +'的查询结果<br />'
        flag = False
        for subnet in subnets:
            if ip in ipaddress.ip_network(subnet.subnet):
                flag = True
                return_txt += '--所属网段：'+ subnet.subnet + '(网络类型:' + subnet.type + ')<br />'
                special_ips = SpecialIp.objects.filter(belonging_subnet=subnet)
                for each_ip in special_ips:
                    return_txt += '----下属特殊地址：'
                    return_txt += each_ip.ip + ':' + each_ip.type + '<br />'
        if not flag:
            return_txt += '没有找到任何匹配的条目，请确保你的查询没有出错！'
        else:
            return_txt += '<br /><br /><br />配置服务器提示：<br / ><ol>' \
                          '<li>对于在负载均衡设备后且未做三角传输的服务，服务器需要将默认路由指向负载均衡浮动网关，将192.168.0.0/16指向核心交换机浮动网关</li>' \
                          '<li>对于公网网段，默认路由指向运营商网关或核心交换机浮动网关</li>' \
                          '<li>其他特殊场景应用，请咨询网络组</li></ol>'
        return HttpResponse(return_txt)