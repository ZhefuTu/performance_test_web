# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from perf_show import get_result_info, get_table_html, get_options_html
from release_test_result import get_release_result, get_module_heads
import json
import os
from mit_server import get_top_cases_html

# Create your views here.

def index(request):
    context = {}
    return render(request, 'DataShow/chart.html', context)

def empty(request):
    context = {}
    return render(request, 'DataShow/empty.html', context)

def show_performance_test(request):
    os.system('bash ./DataShow/download_perf_data.sh')
    context = {}
    # context['batch_query'] = get_result_info()
    return render(request, 'DataShow/performance_test.html', context)


def get_perf_data(request):
    if request.method == 'GET':
        node = request.GET.get('node')
        kind = request.GET.get('kind')
        # cpu = str(request.GET.get('cpu', 'all'))
        # mem = str(request.GET.get('mem', 'all'))
        platform = [request.GET.get('platform', '')]
        platform = request.GET.getlist('platform[]', 'all')
        # count = str(request.GET.get('count', 'all'))
        version = request.GET.getlist('version[]', 'all')
        query_name = request.GET.getlist('query[]', ['bi_1'])
        args = {'platform':platform, 'version':version, "query_name": query_name}
        result = {}
        result['x_name'] = 'version'
        data_info, max_time, platform_options, version_options, query_options = get_result_info(kind, node, args)
        result['xa'] = data_info[0]
        result['ya'] = data_info[1]

        result['data'] = []
        data_len = len(data_info) - 2
        for i in range(data_len):
            result['data'].append([])
        for i in range(len(data_info[0])):
            for j in range(data_len):
                result['data'][j].append({'value': data_info[
                    j + 2][i], 'date': data_info[0][i]})
        result['max_time'] = max_time
        # result["table_html"] = get_table_html(data_info, kind, node)
        result['option_html'] = get_options_html(kind, node, platform_options, version_options, query_options, platform, version, query_name)
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json,charset=utf-8")

def show_release_test(request):
    context = {}
    context['th_content'] = mark_safe(get_module_heads())
    context['table_content'] = mark_safe(get_release_result())
    return render(request, 'DataShow/release_test_result.html', context)

def show_report(request):
    file_path = request.GET.get("file_path","")
    if os.path.isfile(file_path):
        result = ""
        f= open(file_path, "r")
        data = f.readlines()
        for line in data:
            result += "<span>%s</span><br>"%line
        return HttpResponse(result)
    elif os.path.isdir(file_path):
        files = os.listdir(file_path)
        result = ""
        for file in files:
            f = open(os.path.join(file_path, file), "r")
            data = f.readlines()
            result += '<br><br><span style="background-color:yellow">File: %s</span><br>'%file
            result += "<br>".join(data)
        return HttpResponse(result)
    else:
        return HttpResponse("No file path given!")

def get_top_cases(request):
    days = request.GET.get("days", 30)
    typ = request.GET.get("type", "failed")
    exclude = request.GET.get("exclude", "false")
    context = {}
    context['days'] = days
    context['type'] = typ
    context['exclude'] = exclude
    context['content'] = mark_safe(get_top_cases_html(days, typ, exclude))
    return render(request, 'DataShow/top_cases.html', context)
