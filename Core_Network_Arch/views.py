from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from .models import *
from django.utils import timezone
from Module.Core_Network_Arch.cacti import CactiDataAnalyzer
from django.contrib.auth.decorators import login_required,permission_required
import json
import datetime
import threading
import collections


# Create your views here.

class IndexView(generic.ListView):
    template_name = 'Core_Network_Arch/index.html'

    def get_queryset(self):
        return None


class ReportListView(generic.ListView):
    template_name = 'Core_Network_Arch/report_list_view.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return TrafficStatsReport.objects.order_by('-id')


class ReportDetailView(generic.ListView):
    context_object_name = 'report_details'
    template_name = 'Core_Network_Arch/traffic_report.html'

    def get_queryset(self):
        link_list = []
        report = TrafficStatsReport.objects.get(id=self.args[0])
        farms = Farm.objects.order_by('-display_priority')
        print(farms)
        detail_dict = collections.OrderedDict()
        stats = TrafficStat.objects.filter(associated_report=report.id).order_by('name')
        devices = Device.objects.all()
        for farm in farms:
            detail_dict[farm.type] = {}

        for device in devices:
            if device.name not in detail_dict[device.environment.type]:
                detail_dict[device.environment.type][device.name] = []
        for stat in stats:
            detail_dict[stat.link.device.filter(devicelinkmember__data_source=True)[0].environment.type][stat.link.device.filter(devicelinkmember__data_source=True)[0].name].append(stat)
            if stat.link not in link_list:
                link_list.append(stat.link)
        print(detail_dict)
        return dict(report=report, detail_dict=detail_dict,links=link_list)


class SettingsMainView(generic.ListView):
    template_name = 'Core_Network_Arch/settings.html'
    context_object_name = 'settings'

    def get_queryset(self):
        return dict(type=Farm.objects.order_by('-id'), device=Device.objects.order_by('-id'),
                    link=Link.objects.order_by('-id'), device_layer_type=DeviceLayerType.objects.order_by('-id'),
                    trafficstatsReport=TrafficStatsReport.objects.order_by('-id'))


class TrafficStatsDetailView(generic.DetailView):
    template_name = 'Core_Network_Arch/traffic_stats_detail.html'
    model = TrafficStat


def json_traffic_data(request, pk):
    traffic_data = get_object_or_404(TrafficStat, pk=pk)
    if request.method == 'GET':
        # traffic_stats = get_object_or_404(TrafficStats, pk=traffic_stats_id)
        response_data = traffic_data.traffic_sequence
        return HttpResponse(json.dumps({'sequence': eval(response_data), 'month': 6}), content_type='application/json')


def json_traffic_data_bulk(request):
    if request.method == 'GET':
        bulk_list = []
        traffic_datas = TrafficStat.objects.filter(link=request.GET['link_id'],
                                                   associated_report=request.GET['report_id'])
        for traffic_data in traffic_datas:
            temp_sequence = eval(traffic_data.traffic_sequence)
            for sequence in temp_sequence:
                bulk_list.append(sequence)
        return HttpResponse(json.dumps({'sequence': bulk_list, 'month': 6}), content_type='application/json')


def create_single_traffic_data(request):
    if request.method == 'GET':
        if len(TrafficStat.objects.filter(start_time=datetime.datetime.fromtimestamp(float(request.GET['starttime'])),
                                          end_time=datetime.datetime.fromtimestamp(float(request.GET['endtime'])),
                                          stats_interval=request.GET['interval'],
                                          data_source=request.GET['cacti_id'],
                                          link=request.GET['link_id']
                                          )) != 0:
            return HttpResponse('Duplicate traffic stats.')
        if CactiServer.objects.get(pk=request.GET['cacti_id']) is None:
            return HttpResponse('No registered Cacti Server with id %s' % request.GET['cacti_id'])
        if Link.objects.get(pk=request.GET['link_id']) == 0:
            return HttpResponse('No registered Link with id %s' % request.GET['link'])
        if request.GET['year'] is None or request.GET['month'] is None:
            return HttpResponse('No specified month or year')
        else:
            starttime = datetime.datetime.fromtimestamp(float(request.GET['starttime']))
            endtime = datetime.datetime.fromtimestamp(float(request.GET['endtime']))
            cacti_server = CactiServer.objects.get(pk=request.GET['cacti_id'])
            link = Link.objects.get(pk=request.GET['link_id'])
            cactidataanalyzer = CactiDataAnalyzer()
            cactidataanalyzer.collect_cacti_data_monthly(cacti_server.ip, cacti_server.username,
                                                         cacti_server.password, link.graph_id,
                                                         request.GET['year'], request.GET['month'],
                                                         cacti_server.port)
            new_avg_traffic_stats = TrafficStat(
                name='%s-%s-%s@%s-avg' % (link.name, starttime, endtime, cacti_server.name),
                associated_report=None, data_source=cacti_server, link=link,
                start_time=starttime, end_time=endtime,
                stats_interval=request.GET['interval'], type='avg',
                traffic_sequence=cactidataanalyzer.get_avg_sequence())
            new_max_traffic_stats = TrafficStat(
                name='%s-%s-%s@%s-max' % (link.name, starttime, endtime, cacti_server.name),
                associated_report=None,
                data_source=cacti_server, link=link,
                start_time=starttime, end_time=endtime,
                stats_interval=request.GET['interval'], type='max',
                traffic_sequence=cactidataanalyzer.get_max_sequence())
            new_min_traffic_stats = TrafficStat(
                name='%s-%s-%s@%s-min' % (link.name, starttime, endtime, cacti_server.name),
                associated_report=None,
                data_source=cacti_server, link=link,
                start_time=starttime, end_time=endtime,
                stats_interval=request.GET['interval'], type='min',
                traffic_sequence=cactidataanalyzer.get_min_sequence())
            new_avg_traffic_stats.save()
            new_max_traffic_stats.save()
            new_min_traffic_stats.save()
        return HttpResponse('Successful!')


@permission_required('admin', login_url='/admin/')
def create_monthly_report(request):
    if request.method == 'GET':
        try:
            year = int(request.GET['report_time'].split('-')[0])
            month = int(request.GET['report_time'].split('-')[1])
            print(year,month)
        except ValueError:
            return HttpResponse('Invalid Month and Year!')
        start_time = datetime.datetime(year, month, 1)
        if month == 12:
            end_time = datetime.datetime(year + 1, 1, 1)
        elif month in range(1, 12):
            end_time = datetime.datetime(year, month + 1, 1)
        else:
            return HttpResponse('Invalid Month and Year!')
        if len(TrafficStatsReport.objects.filter(start_time=start_time, end_time=end_time)) != 0:
            return HttpResponse('指定月份的报表已经存在！如果需要重新生成，请于django管理后台删除当前月份报告，再重新生成。')
        created_report = TrafficStatsReport(name='%s年%s月流量资源报表'%(year,month),start_time=start_time, end_time=end_time,description='%s年%s月流量资源报表'%(year,month),stats_interval=86400)
        created_report.save()
        for link in Link.objects.filter(accounting=True):
            t = threading.Thread(target=_create_single_stats_monthly, args=(link, year, month, start_time, end_time,created_report))
            t.start()
        return HttpResponse('已经成功提交生成报告。请等待大约1分钟后打开报表。')


def _create_single_stats_monthly(link, year, month,starttime,endtime,report):
    cactidataanalyzer = CactiDataAnalyzer()
    # print(link)
    print(DeviceLinkMember.objects.filter(data_source=True, link=link))
    designated_source = DeviceLinkMember.objects.filter(data_source=True, link=link)[0]
    cacti_server = designated_source.device.cactiServer
    cactidataanalyzer.collect_cacti_data_monthly(cacti_server.ip, cacti_server.username,
                                                 cacti_server.password, designated_source.graph_id,
                                                 year, month,
                                                 cacti_server.port)
    start_timestamp = datetime.datetime(year, month, 1).timestamp()
    new_max_traffic_stats = TrafficStat(
                name='%s-%s-%s@%s-max' % (link.name, starttime, endtime, cacti_server.name),
                associated_report=report,
                data_source=cacti_server, link=link,
                start_time=starttime, end_time=endtime,
                stats_interval=86400, type='max',
                traffic_sequence=cactidataanalyzer.get_max_sequence())
    new_min_traffic_stats = TrafficStat(
                name='%s-%s-%s@%s-min' % (link.name, starttime, endtime, cacti_server.name),
                associated_report=report,
                data_source=cacti_server, link=link,
                start_time=starttime, end_time=endtime,
                stats_interval=86400, type='min',
                traffic_sequence=cactidataanalyzer.get_min_sequence())
    new_avg_traffic_stats = TrafficStat(
                name='%s-%s-%s@%s-avg' % (link.name, starttime, endtime, cacti_server.name),
                associated_report=report, data_source=cacti_server, link=link,
                start_time=starttime, end_time=endtime,
                stats_interval=86400, type='avg',
                traffic_sequence=cactidataanalyzer.get_avg_sequence())

    new_avg_traffic_stats.save()
    new_max_traffic_stats.save()
    new_min_traffic_stats.save()
    return True
