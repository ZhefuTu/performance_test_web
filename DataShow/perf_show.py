# coding:utf-8

import os
import re
import pprint

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
                    if i > 1200:
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
            except:
                failed_flag = True
                break
        elif kind == 'ldbc_queries':
            try:
                if "Memory usage Average" in line:
                    pass
                elif "Average" in line:
                    cost = float(line.split()[2])
                    max_t = max(max_t, cost)
                    result.append(cost)
                    break
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


def get_machine_info(path):
    result = {"platform":"no-record"}
    if "machine_info" in os.listdir(path):
        f = open(os.path.join(path,"machine_info"), 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            line = line.replace("\n", "")
            # if line.startswith("OS:"):
            #     result['os'] = line.split()[1]
            # elif line.startswith("Memory:"):
            #     result['memory'] = str(int(line.split()[1])/(1024*1024))
            # elif line.startswith("CPU(s):"):
            #     result['vcpu'] = line.split()[1]
            if line.startswith("Platform:"):
                temp = line.split()
                if len(temp) > 1:
                    result['platform'] = temp[1]    
            # elif line.startswith("Count:"):
            #     temp = line.split()
            #     if len(temp) > 1:
            #         result['count'] = line.split()[1]
    return result


def get_result_info(kind='batch_query', node='single', args={}):
    result_info = []
    max_time = 0

    cur_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/perf', node)
    dirs = os.listdir(cur_path)
    dirs.sort(key=dir_sort_by_time)
    platform_options = []
    version_options = []
    query_options = []
    version_count = {}
    for dir in dirs:
        dir_path = os.path.join(cur_path, dir)
        if os.path.isdir(dir_path):          
            version = re.match('.*(\d\.\d\.\d).*', dir)
            if not version or version.group(1) <= '2.5.0':
                continue
            version = version.group(1)
            if version not in version_options:
                version_options.append(version)

            machine_info = get_machine_info(dir_path)
            if machine_info.get('platform', '') not in platform_options:
                platform_options.append(machine_info.get('platform', ''))

            select_platform = machine_info.get('platform', '') in args['platform'] or args['platform'] == "all"
            if not (version in args['version'] or args['version'] == "all"):
                continue
            if not select_platform:
                continue

            if args['platform'] == 'all' and args['version'] == 'all' and version_count.get(version, 0) >= 5:
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
                            file_path, max_time, kind)
                        if len(query_timelist) != 4:
                            continue
                        else:
                            if query_timelist[0] == 10:
                                temp[2] = query_timelist[3]
                            else:
                                temp[3] = query_timelist[3]
                            max_time = max(max_time, max_t)
                if temp[2] != 0 and temp[3] != 0:
                    result_info.append(temp)
                    if version not in version_count:
                        version_count[version] = 0
                    version_count[version] += 1
            elif kind == 'ldbc_queries':
                for file in files:
                    if file.startswith(kind):
                        # time = time_format(file)
                        ldbc_dir = os.path.join(dir_path, file)
                        queries = os.listdir(ldbc_dir)
                        query_options = list(set(queries + query_options))
                        temp = [dir, version]
                        for qn in args.get("query_name", ["bi_1"]):
                            file_path = os.path.join(ldbc_dir, "%s.base"%qn)
                            query_timelist, max_t = read_file(
                                file_path, max_time, kind)
                            if len(query_timelist) != 1:
                                continue
                            temp.extend(query_timelist)
                            max_time = max(max_time, max_t)
                        result_info.append(temp)
                        if version not in version_count:
                            version_count[version] = 0
                        version_count[version] += 1
            else:
                for file in files:
                    if file.startswith(kind):
                        # time = time_format(file)
                        file_path = os.path.join(dir_path, file)
                        temp = [dir, version]
                        query_timelist, max_t = read_file(
                            file_path, max_time, kind)
                        if kind == 'batch_query' and len(query_timelist) != 4:
                            continue
                        elif kind == 'normal_load' and len(query_timelist) != 4:
                            continue
                        elif kind == 'hub_load' and len(query_timelist) != 1:
                            continue
                        temp.extend(query_timelist)
                        result_info.append(temp)
                        max_time = max(max_time, max_t)
                        if version not in version_count:
                            version_count[version] = 0
                        version_count[version] += 1
    result = []
    if result_info:
        data_len = len(result_info[0])
        # result_info = result_info[-50:]
        for i in range(data_len):
            result.append([])
        for info in result_info:
            for i in range(len(result)):
                result[i].append(info[i])
    max_time = ((int(max_time) / 1) + 1) * 1
    for i in range(len(query_options)):
        query_options[i] = query_options[i].replace(".base", "")
    query_options.sort()
    version_options.sort(reverse=True)
    return result, max_time, platform_options, version_options, query_options

def get_options_html(kind, node, platform_options, version_options, query_options, platform, version, query_name):
    html = ""
    if kind == "ldbc_queries":
        html += '<div class="ui basic label">Query</div><select class="ui fluid dropdown query" multiple="" id="%s_%s_query" onchange="draw_new(\'%s\', \'%s\')">'%(kind, node, kind, node)
        for opt in query_options:
            if opt in query_name:
                html += '<option class="item" value="%s" selected>%s</option>'%(opt, opt)
            else:
                html += '<option class="item" value="%s">%s</option>'%(opt, opt)
        html += '</select>'
    html += '<div class="ui basic label">Version</div><select class="ui fluid dropdown version" multiple="" id="%s_%s_version" onchange="draw_new(\'%s\', \'%s\')">'%(kind, node, kind, node)
    for opt in version_options:
        if opt in version:
            html += '<option class="item" value="%s" selected>%s</option>'%(opt, opt)
        else:
            html += '<option class="item" value="%s">%s</option>'%(opt, opt)
    html += '</select>'
    html += '<div class="ui basic label">Platform</div><select class="ui fluid dropdown platform" multiple="" id="%s_%s_platform" onchange="draw_new(\'%s\', \'%s\')">'%(kind, node, kind, node)
    for opt in platform_options:
        if opt in platform:
            html += '<option class="item" value="%s" selected>%s</option>'%(opt, opt)
        else:
            html += '<option class="item" value="%s">%s</option>'%(opt, opt)
    html += '</select>'
    html += '<div class="ui negative button" onclick="clear_options(\'%s\', \'%s\')">Clear</div>'%(kind, node)
    return html


def get_table_html(result, kind, node):
    html = ""
    html = "<table class='table table-hover table-bordered'><tr><th>%s</th>"%node
    for version in result[1]:
        html += "<th>%s</th>" %version
    if kind == "batch_query":
        # non batch wcc
        html += "</tr><tr><td>wcc</td>"
        for info in result[2]:
            html += "<td>%s</td>"%info
        # non batch pagerank
        html += "</tr><tr><td>pagerank</td>"
        for info in result[3]:
            html += "<td>%s</td>"%info
        # non batch wcc
        html += "</tr><tr><td>distributed wcc</td>"
        for info in result[4]:
            html += "<td>%s</td>"%info
        # non batch wcc
        html += "</tr><tr><td>distributed pagerank</td>"
        for info in result[5]:
            html += "<td>%s</td>"%info
    elif kind == "normal_load" and node == "single":
        html += "</tr><tr><td>tpch load</td>"
        for info in result[5]:
            html += "<td>%s</td>"%info
    elif kind == "normal_load" and node == "cluster":
        html += "</tr><tr><td>tpch load 10GB</td>"
        for info in result[2]:
            html += "<td>%s</td>"%info
        # non batch pagerank
        html += "</tr><tr><td>tpch load 30GB</td>"
        for info in result[3]:
            html += "<td>%s</td>"%info
    elif kind == "hub_load":
        html += "</tr><tr><td>hub load</td>"
        for info in result[2]:
            html += "<td>%s</td>"%info
    html += "</tr></table>"
    return html


if __name__ == "__main__":
    result1 = get_result_info('ldbc_queries','single',{'platform':'GCP','version':'all', 'query_name':["bi_1","bi_10","bi_9"]})

    result2 = get_result_info('batch_query','single',{'platform':'GCP','version':'all'})
    # temp = result[4]
    # temp.sort()
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(result1[0])
    # print result2[0][3]