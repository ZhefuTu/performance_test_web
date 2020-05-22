# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from perf_show import get_result_info
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

        batch_query, max_time = get_result_info(kind)
        batch_query_info = batch_query[node]
        result['xa'] = batch_query_info[0]
        result['ya'] = batch_query_info[1]

        result['data'] = []
        data_len = len(batch_query_info) - 2
        for i in range(data_len):
            result['data'].append([])
        for i in range(len(batch_query_info[0])):
            for j in range(data_len):
                result['data'][j].append({'value': batch_query_info[
                                 j + 2][i], 'date': batch_query_info[0][i]})
        result['max_time'] = max_time[node]
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json,charset=utf-8")
