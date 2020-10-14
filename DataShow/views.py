# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from perf_show import get_result_info, get_table_html
from release_test_result import get_release_result
import json
import os

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
        result = {}
        result['x_name'] = 'version'

        data_info, max_time = get_result_info(kind, node)
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
        result["table_html"] = get_table_html(data_info, kind, node)
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json,charset=utf-8")

def show_release_test(request):
    context = {}
    context['table_content'] = mark_safe(get_release_result())
    return render(request, 'DataShow/release_test_result.html', context)

def show_report(request):
    file_path = request.GET.get("file_path","")
    if file_path:
        f= open(file_path, "r")
        data = f.readlines()
        data = "<br>".join(data)
        return HttpResponse(data)
    else:
        return HttpResponse("No file path given!")