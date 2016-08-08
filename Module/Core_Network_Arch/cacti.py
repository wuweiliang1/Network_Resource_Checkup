import urllib.request
import http.cookiejar
import urllib.parse
import re
import time
import calendar
from datetime import date, datetime


# def collect_cacti_data(server, username, password, graph_id, raw_starttime, raw_endtime, port=80):
#     opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
#     opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
#     auth_data = urllib.parse.urlencode({'action': 'login', 'login_username': username, 'login_password': password})
#     login_page = 'http://%s:%s/index.php' % (server, port)
#     opener.open(login_page, auth_data.encode('UTF-8'))
#     starttime = int(raw_starttime) - 1
#     currtime = starttime
#     endtime = int(raw_endtime)
#     buffer = ''
#     while currtime <= endtime:
#         xport_page = 'http://%s:%s/graph_xport.php?local_graph_id=%s&graph_start=%s&graph_end=%s' % (
#             server, port, graph_id, currtime, currtime + 3600)
#         response = opener.open(xport_page)
#         buffer += str(response.read().decode('UTF-8').split('\n')[10:])
#         currtime += 3600
#     return buffer


class CactiDataAnalyzer:
    def __init__(self):
        self.rawdata = None
        self.starttimestamp = None
        self.endtimestamp = None
        self.interval = None
        self.input_column_map = {}
        self._max_analysis_data = []
        self._min_analysis_data = []
        self._avg_analysis_data = []

    def get_max_sequence(self):
        temp_column_data_list = []
        for column in self.input_column_map:
            temp_column_data_dict = {'name': column+'-max', 'data': []}
            # Construct the max_dict for output
            for timestamp in sorted(self.rawdata):
                temp_column_data_dict['data'].append(int(
                    max(self.rawdata[timestamp][column])))
            temp_column_data_list.append(temp_column_data_dict)
        self._max_analysis_data = temp_column_data_list
        return self._max_analysis_data

    def get_min_sequence(self):
        temp_column_data_list = []
        for column in self.input_column_map:
            temp_column_data_dict = {'name': column+'-min', 'data': []}
            # Construct the max_dict for output
            for timestamp in sorted(self.rawdata):
                temp_column_data_dict['data'].append(int(
                    min(self.rawdata[timestamp][column])))
            temp_column_data_list.append(temp_column_data_dict)
        self._min_analysis_data = temp_column_data_list
        return self._min_analysis_data

    def get_avg_sequence(self):
        temp_column_data_list = []
        for column in self.input_column_map:
            temp_column_data_dict = {'name': column+'-avg', 'data': []}
            # Construct the max_dict for output
            for timestamp in sorted(self.rawdata):
                temp_column_data_dict['data'].append(int(
                    sum(self.rawdata[timestamp][column]) / len(
                        self.rawdata[timestamp][column])))
            temp_column_data_list.append(temp_column_data_dict)
        self._avg_analysis_data = temp_column_data_list
        return self._avg_analysis_data

    def collect_cacti_data_monthly(self, server, username, password, graph_id, year, month, port=80):
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
        auth_data = urllib.parse.urlencode({'action': 'login', 'login_username': username, 'login_password': password})
        login_page = 'http://%s:%s/index.php' % (server, port)
        opener.open(login_page, auth_data.encode('UTF-8'))
        year = int(year)
        month = int(month)
        self.starttimestamp = datetime(year, month, 1).timestamp()
        if month in range(1,12):
            self.endtimestamp = datetime(year, month + 1, 1).timestamp()
        elif month == 12:
            self.endtimestamp = datetime(year+1, 1, 1).timestamp()
        self.interval = 3600 * 24
        times = int((self.endtimestamp - self.starttimestamp) / self.interval)
        analysis_dict = {}
        parameter_count = 0
        for i in range(times):
            xport_page = 'http://%s:%s/graph_xport.php?local_graph_id=%s&graph_start=%s&graph_end=%s' % (
                server, port, graph_id, int(self.starttimestamp + i * self.interval),
                int(self.starttimestamp + (i + 1) * self.interval))
            response = opener.open(xport_page)
            timestamp = int(self.starttimestamp + i * self.interval)
            analysis_dict[timestamp] = {}
            if len(self.input_column_map) > 0:
                for key in self.input_column_map:
                    analysis_dict[timestamp][key] = []
            for rawitem in response.read().decode('UTF-8').split('\n'):
                item = rawitem.replace('"', '')
                if i == 0 and (re.search(r'^Date', item) is not None):
                    parameter_count = len(item.split(',')) - 1
                    header = re.search(r'Date(?:' + (',([^,]*)' * parameter_count) + ')$', item)
                    for j in range(parameter_count):
                        self.input_column_map[header.group(j + 1)] = j + 1
                        analysis_dict[timestamp][header.group(j + 1)] = []
                    continue
                reengine = re.search(
                    r'[0-9]{4}-[0-1][1-9]-[0-3][0-9] [0-2][0-9]:[0-6][0-9]:[0-6][0-9](?:' + ',([^,]*)' * parameter_count + ')$',
                    item)
                if reengine is not None:
                    for column in self.input_column_map:
                        if reengine.group(int(self.input_column_map[column])) == 'NaN':
                            continue
                        analysis_dict[timestamp][column].append(float(reengine.group(int(self.input_column_map[column]))))
                else:
                    continue
        self.rawdata = analysis_dict
        return True

#
# cacti_analyzer = CactiDataAnalyzer()
# cacti_analyzer.collect_cacti_data_monthly('192.168.232.20', 'admin', 'PConline', 6647, 2016, 6, port=8080)
# print(cacti_analyzer.get_max_sequence())
# print(cacti_analyzer.get_min_sequence())
# print(cacti_analyzer.get_avg_sequence())
# print(cacti_analyzer.get_each_avg())
