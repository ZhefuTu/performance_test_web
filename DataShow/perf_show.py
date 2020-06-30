# coding:utf-8

import os
import re

TEST_DATA_PATH = "./perf"


def convert_time(t):
    h = 0
    if 'h' in t:
        h = float(t.split('h')[0])
        t = t.split('h')[1]
    m = 0
    if 'm' in t:
        m = float(t.split('m')[0])
        t = t.split('m')[1]
    s = float(t.replace('s', ''))
    return float('%.2f' % (3600 * h + 60 * m + s))


def read_file(path, max_time, kind):
    f = open(path, 'r')
    data = f.readlines()
    f.close()
    failed_flag = False
    index = 0
    result = []
    max_t = max_time
    while index < len(data):
        line = data[index]
        if 'FAILED' in line:
            failed_flag = True
            break
        if kind == 'batch_query':
            if 'Non batch mode query' in line or 'Non distributed mode query' in line:
                try:
                    for delta in [2, 5, 7, 5]:
                        index += delta
                        line = data[index]
                        time_cost = line.split('\t')[1]
                        time_cost = time_cost.replace('\n', '')
                        time_cost = convert_time(time_cost)
                        max_t = max(max_t, time_cost)
                        result.append(time_cost)
                except:
                    failed_flag = True
                    break
                if sum(result) < 4:
                    failed_flag = True
                    break
                for i in result:
                    if i > 850:
                        failed_flag = True
                        break
        elif kind == 'normal_load':
            try:
                if 'Normal loading of tpch data with scale factor' in line:
                    scale = int(line.split(
                        ':')[1].replace('\n', '').strip())
                    result.append(scale)
                if 'Total Lines' in line:
                    total_lines = int(line.split(
                        ':')[1].replace('\n', '').strip())
                    result.append(total_lines)
                if 'Total time' in line:
                    total_time = int(line.split(
                        ':')[1].replace('\n', '').strip())
                    result.append(total_time)
                if 'Average speed' in line:
                    avg_speed = int(line.split(
                        ':')[1].replace('\n', '').strip())
                    result.append(avg_speed)
                    max_t = max(max_t, avg_speed)
            except:
                failed_flag = True
                break
        elif kind == 'hub_load':
            try:
                if '/1.csv' in line:
                    pattern = re.compile('.* (\d*) kl/s.*')
                    speed = int(re.match(pattern, line).group(1))
                    max_t = max(max_t, speed)
                    result.append(speed)
                    break
                # if 'bigtest/tests/loading/dataset/2.csv' in line:
                #     pattern = re.compile('.* (\d*) kl/s.*')
                #     speed = int(re.match(pattern, line).group(1))
                #     max_t = max(max_t, speed)
                #     result.append(speed)
            except:
                failed_flag = True
                break
        index += 1
    if failed_flag:
        return [], 0
    return result, max_t

def dir_sort_by_time(f):
    time_p = re.match('.*(\d{2}-\d{2}-\d{4}).*', f)
    ver_p = re.match('.*(\d\.\d\.\d).*', f)
    if time_p and ver_p:
        t = time_p.group(1)
        v = ver_p.group(1)
        t = t.split('-')
        result = v + t[2] + t[0] + t[1]
    else:
        result = ''
    return result


def time_format(file_path):
    t = file_path.split('_')[-2:]
    return '%s %s' % (t[0], ':'.join(t[1].split('-')[:2]))


def get_result_info(kind='batch_query'):
    nodes = ['single', 'cluster']
    result_info = {'single': [], 'cluster': []}
    max_time = {'single': 0, 'cluster': 0}
    for node in nodes:
        cur_path = os.path.join(TEST_DATA_PATH, node)
        print os.listdir('./')
        dirs = os.listdir(cur_path)
        dirs.sort(key=dir_sort_by_time)
        for dir in dirs:
            dir_path = os.path.join(cur_path, dir)
            if os.path.isdir(dir_path): 
                version = '_'.join(dir.split('release')[-1].split('_')[1:-1])
                # version = '_'.join(dir.split('_')[1:-1])

                version_num = re.match('.*(\d\.\d\.\d).*', dir)
                if not version_num or version_num.group(1) <= '2.2.0':
                    continue
                files = os.listdir(dir_path)
                if node == 'cluster' and kind == 'normal_load':
                    temp = [dir, version, 0, 0]
                    for file in files:
                        if file.startswith(kind):
                            # time = time_format(file)
                            file_path = os.path.join(dir_path, file)
                            # temp[0] = time
                            query_timelist, max_t = read_file(
                                file_path, max_time[node], kind)
                            if len(query_timelist) != 4:
                                continue
                            else:
                                if query_timelist[0] == 10:
                                    temp[2] = query_timelist[3]
                                else:
                                    temp[3] = query_timelist[3]
                                max_time[node] = max(max_time[node], max_t)
                    result_info[node].append(temp)
                else:
                    for file in files:
                        if file.startswith(kind):
                            # time = time_format(file)
                            file_path = os.path.join(dir_path, file)
                            temp = [dir, version]
                            query_timelist, max_t = read_file(
                                file_path, max_time[node], kind)
                            if kind == 'batch_query' and len(query_timelist) != 4:
                                continue
                            elif kind == 'normal_load' and len(query_timelist) != 4:
                                continue
                            elif kind == 'hub_load' and len(query_timelist) != 1:
                                continue
                            temp.extend(query_timelist)
                            result_info[node].append(temp)
                            max_time[node] = max(max_time[node], max_t)
    single_len = len(result_info['single'][0])
    cluster_len = len(result_info['cluster'][0])
    result = {'single': [], 'cluster': []}
    for i in range(single_len):
        result['single'].append([])
    for i in range(cluster_len):
        result['cluster'].append([])
    for k, v in result_info.iteritems():
        for info in v:
            for i in range(len(result[k])):
                result[k][i].append(info[i])
    for k in max_time.keys():
        max_time[k] = ((int(max_time[k]) / 10) + 1) * 10
    return result, max_time
