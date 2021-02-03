# coding:utf-8

import re
import os
import hashlib

MODULE_HEADS = [
    "install",
    "create_schema",
    "load_data",
    "deletion",
    "schema_change",
    "batch_query",
    "tpch_load",
    "hub_load",
    "backup",
    "restore",
    "tpch_queries",
    "ldbc_queries",
    "secondary_index",
    "update_test",
    "gsql_stress",
    "gse_compaction_enable",
    "query_installation",
    "concurrent_load",
    "upgrade",
    "clear_graph_store",
    "database_export",
    "database_import",
    "kafka_load",
    "ldap",
    "ssl_config",
    "token_config",
    "cross_region_replication",

    "stress_test",
    # "wcc_pagerank",
    # "service_failure",
    # "service_recover",
    # "gse_compaction_disable",
]

# RESULT_DIR="E:/work/release_test_result"
# PERFORMANCE_DIR="E:/work/performance_test_web/perf"
RESULT_DIR="/home/graphsql/release_test_result"
PERFORMANCE_DIR="/home/graphsql/performance_test_web/perf"

def get_module_heads():
    html_content = ""
    for module in MODULE_HEADS:
        html_content += '<th class="center aligned">%s</th>'%(" ".join(module.split("_")))
    return html_content

def get_module_name(file_name, file_path):
    if os.path.isfile(file_path):
        if file_name.startswith("install_") and file_name.endswith("_result"):
            return "install"
        elif file_name.endswith("_result"):
            prefix = file_name.replace("_result", "")
            if prefix in ["schema_change","backup","restore","query_installation","concurrent_load","upgrade","clear_graph_store","database_export","database_import","kafka_load","ldap","ssl_config","create_schema","load_data","deletion","stress_test"]:
                return prefix
            elif prefix == "index":
                return "secondary_index"
            elif prefix == "token_enable":
                return "token_config"
            elif prefix == "CRR_config":
                return "cross_region_replication"
            elif prefix == "update":
                return "update_test"
        elif file_name.startswith("wcc_pagerank_"):
            return "wcc_pagerank"
        elif file_name.startswith("gse_compaction_enable"):
            return "gse_compaction_enable"
        elif file_name.startswith("batch_query_"):
            return "batch_query"
        elif file_name.startswith("hub_load_"):
            return "hub_load"
        elif file_name.startswith("normal_load_10_"):
            return "tpch_load"
    else:
        if file_name == "gsql_stress_result":
            return "gsql_stress"
        elif file_name in ["tpch_queries","ldbc_queries"]:
            return file_name
    return ""

def get_module_result(module_name, file_path):
    if os.path.isfile(file_path):
        f = open(file_path, "r")
        data = f.readlines()
    # return list 
    # r_str: pass or failed or blank : string
    # s_result: simple result : string'
    # file_path: result file path : string
    if module_name == "install":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "Installation Finished" in line:
                r_str = "Pass"
            if "installation finished" in line:
                s_result = line.split(" ")[3] + " s"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "create_schema":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if line.startswith("The graph") and "is created." in line:
                r_str = "Pass"
            if "Cost time" in line:
                s_result = line.split(" ")[2] + " s"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "deletion":
        r_str = "Failed"
        s_result = ""
        flag_count = 0
        for line in data:
            check_string = ['"error":false', 'check passed']
            for s in check_string:
                if s in line:
                    flag_count += 1
            if flag_count == len(check_string) + 1:
                r_str = "Pass"
            if "Deletion cost time" in line:
                s_result = line.split(" ")[3] + " s"
        if r_str == "Failed":
            s_result = ""
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "gse_compaction_enable":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "ENABLE_LOCAL_DB=1" in line:
                r_str = "Pass"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "load_data":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "FINISHED" in line:
                r_str = "Pass"
            if "Load data cost time" in line:
                s_result = line.split(" ")[4] + " s"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "schema_change":
        r_str = "Failed"
        s_result = ""
        flag_count = 0
        for line in data:
            check_string = ["The job add_test_node completes in", "The job drop_test_node completes in", "FINISHED", "The job add_attr completes in", "check passed"]
            for s in check_string:
                if s in line:
                    flag_count += 1
                    break
            if flag_count == len(check_string):
                r_str = "Pass"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "secondary_index":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "schema change succeeded" in line:
                r_str = "Pass"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "ldap":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "Name: qa_test" in line:
                r_str = "Pass"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "update_test":
        r_str = "Pass"
        s_result = ""
        for line in data:
            if '"error":true' in line:
                r_str = "Failed"
                break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "upgrade":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if 'Congratulations! Upgrade Finished!' in line:
                r_str = "Pass"
                break
            elif 'gui server is up' in line:
                r_str = "Pass"
                break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "token_config":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if '"error":false' in line:
                r_str = "Pass"
                break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "ssl_config":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if '<title>GraphStudio</title>' in line:
                r_str = "Pass"
                break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "cross_region_replication":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if line:
                r_str = "Pass"
                break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "gsql_stress":
        report_file = os.path.join(file_path, "gsql_stress_result")
        r_str = "Pass"
        s_result = ""
        if os.path.isfile(report_file):
            f = open(report_file, "r")
            data = f.readlines()
            for line in data:
                if 'failed' in line:
                    r_str = "Failed"
                    break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "stress_test":
        report_file = os.path.join(file_path, "stress_test_result")
        r_str = "Pass"
        s_result = ""
        if os.path.isfile(report_file):
            f = open(report_file, "r")
            data = f.readlines()
            for line in data:
                if 'failed' in line:
                    r_str = "Failed"
                    break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "tpch_queries" or module_name == "ldbc_queries":
        report_files = os.listdir(file_path)
        r_str = "Pass"
        s_result = ""
        for file in report_files:
            report_path = os.path.join(file_path, file)
            if os.path.isfile(report_path) and report_path.endswith(".base"):
                flag_temp = False
                f = open(report_path, "r")
                data = f.readlines()
                for line in data:
                    if 'Average' in line:
                        flag_temp = True
                        break
            if not flag_temp:
                r_str = "Failed"
                break
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "hub_load":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if 'FINISHED' in line:
                r_str = "Pass"
            if "1.csv" in line:
                try:
                    pattern = re.compile('.* (\d*) kl/s.*')
                    speed = int(re.match(pattern, line).group(1))
                    s_result = "%d kl/s"%speed
                except:
                    pass
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "batch_query":
        r_str = "Failed"
        s_result = ""
        pass_count = 0
        for line in data:
            if '"error":false' in line:
                pass_count += 1
        if pass_count == 4:
            r_str = "Pass"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "tpch_load":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if 'Total Lines: 86586082' in line:
                r_str = "Pass"
            if 'Average speed:' in line and r_str == "Pass":
                s_result = line.split(" ")[2] + "l/s"
        return [r_str, s_result, file_path.replace("\\","/")]
    elif module_name == "query_installation":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "simple query installation finished" in line:
                r_str = "Pass"
            if "simple query installation finished" in line:
                s_result = line.split("cost")[-1]
        return [r_str, s_result, file_path.replace("\\", "/")]
    elif module_name == "concurrent_load":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "concurrent load finished" in line:
                r_str = "Pass"
            if "concurrent load finished" in line:
                s_result = line.split("cost")[-1]
        return [r_str, s_result, file_path.replace("\\", "/")]
    elif module_name == "backup":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "finished in" in line:
                r_str = "Pass"
            if "finished in" in line:
                s_result = line.split(" ")[-1].replace(".", "")
        return [r_str, s_result, file_path.replace("\\", "/")]
    elif module_name == "restore":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "finished in" in line:
                r_str = "Pass"
            if "finished in" in line:
                s_result = line.split(" ")[-1].replace(".", "")
        return [r_str, s_result, file_path.replace("\\", "/")]
    elif module_name == "database_export":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "export finished" in line:
                r_str = "Pass"
            if "export finished" in line:
                s_result = line.split("cost ")[-1]
        return [r_str, s_result, file_path.replace("\\", "/")]
    elif module_name == "database_import":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "check result PASS" in line:
                r_str = "Pass"
            if "import finished" in line:
                s_result = line.split("cost ")[-1]
        return [r_str, s_result, file_path.replace("\\", "/")]
    elif module_name == "clear_graph_store":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "graph store cleared" in line:
                r_str = "Pass"
            if "graph store cleared" in line:
                s_result = line.split(",")[0].split("in")[-1]
        return [r_str, s_result, file_path.replace("\\", "/")]
    elif module_name == "kafka_load":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "kafka loading finished" in line:
                r_str = "Pass"
            if "kafka loading finished" in line:
                s_result = line.split("cost ")[-1]
        return [r_str, s_result, file_path.replace("\\", "/")]
    return ["", "", ""]

def get_time(tag):
    return tag.split("+")[1]

def index_sort(info):
    index_front = []
    index_behind = []
    for i in info.keys():
        if "+" in i:
            index_behind.append(i)
        else:
            index_front.append("%s+%s"%(i,info[i]["lastest_time"]))
    index_front.sort(key=get_time, reverse=True)
    for i in range(len(index_front)):
        index_front[i] = index_front[i].split("+")[0]
    index_behind.sort(key=get_time, reverse=True)
    index_front.extend(index_behind)
    return index_front

def get_release_result():
    # return "<tr>"+"<td>pass</td>"*(len(MODULE_HEADS)+1)+"</tr>"
    report_dirs = [RESULT_DIR, os.path.join(PERFORMANCE_DIR, "single"), os.path.join(PERFORMANCE_DIR, "cluster")]
    # {version: {tag_job_id :{module_name:["Pass","cost time:188s","e:/hdhdhdh"]}}}
    result = {}
    for report_dir in report_dirs:
        dirs = os.listdir(report_dir)
        for dir in dirs:
            dir_path = os.path.join(report_dir, dir)
            if not os.path.isdir(dir_path):
                continue
            version = re.match('.*(\d\.\d\.\d).*', dir)
            if not version or version.group(1) < '2.5.0':
                continue
            version = version.group(1)
            if version not in result:
                result[version] = {}
            time = re.match('.*(\d\d-\d\d-\d\d\d\d).*', dir)
            if not time:
                continue
            time = time.group(1)

            files = os.listdir(dir_path)
            if "gadmin_version" in files:
                check_sum, lastest_time, gadmin_info = get_version_checksum_and_time(os.path.join(dir_path, "gadmin_version"))
                index = "%s_%s"%(version, check_sum)
                if index not in result[version]:
                    result[version][index] = {"lastest_time": lastest_time, "gadmin_info": gadmin_info}
            else:
                if "single" in dir_path or "cluster" in dir_path:
                    if "single" in dir_path:
                        mode = "single"
                    else:
                        mode = "cluster"
                    test_plan = "performance_%s"%mode
                    index = "%s+%s"%(test_plan, time)
                    if index not in result[version]:
                        result[version][index] = {}
                    else:
                        for i in range(10):
                            if "%s_%d"%(index, i) not in result[version]:
                                index = "%s_%d"%(index, i)
                                break
                        result[version][index] = {}
                else:
                    test_plan = dir.split('_release')[0]
                    job_id = dir.split('_')[-1]
                    index = "%s+%s+%s"%(test_plan, time, job_id)
                    if index not in result[version]:
                        result[version][index] = {}
            for file_name in files:
                file_path = os.path.join(dir_path, file_name)
                module_name = get_module_name(file_name, file_path)
                if module_name:
                    module_result = get_module_result(module_name, file_path)
                    result[version][index][module_name] = module_result

    ver_list = result.keys()
    ver_list.sort(reverse=True)

    html_content = ""
    for ver in ver_list:
        html_ver_tr = [""] * (len(MODULE_HEADS)+1)
        html_ver_tr[0] = ver
        # index_list = result[ver].keys()
        index_list = index_sort(result[ver])
        # index_list.sort(key=get_time, reverse=True)
        index_list = index_list[0:21]
        html_tag_tbody = []
        for ind in index_list:
            html_tag_tr = [""] * (len(MODULE_HEADS)+1)
            module_info = result[ver][ind]
            if "+" in ind:
                html_tag_tr[0] = ind.split("+")[0] + " " + ind.split("+")[1]
            else:
                # html_tag_tr[0] = ind[:16]
                #html_tag_tr[0] = '<a data-toggle="tooltip" data-html="true" data-placement="right" title="%s">%s</a>'%(module_info['gadmin_info'],ind[:16])
                html_tag_tr[0] = module_info['gadmin_info']
            for i in range(len(MODULE_HEADS)):
                mod = MODULE_HEADS[i]
                if mod in module_info:
                    html_tag_tr[i+1] = module_info[mod]
                    if html_ver_tr[i+1] == "":
                        html_ver_tr[i+1] = module_info[mod]
            html_tag_tbody.append(html_tag_tr)

        html_content += '<tr class="active">'
        for i in range(len(html_ver_tr)):
            td = html_ver_tr[i]
            if i == 0:
                html_content += '<td>%s</td>'%get_version_button(td)
            else:
                html_content += '<td>%s</td>'%get_td_html(td)
        html_content += "</tr>"

        html_content += '<tbody class="childrens">'
        for info in html_tag_tbody:
            html_content += "<tr>"
            for td in info:
                if str(td).startswith("<div"):
                    html_content += "<td>%s</td>"%td
                else:
                    if not td:
                        td = "" 
                    html_content += "<td>%s</td>"%get_td_html(td)
            html_content += "</tr>"
        html_content += '</tbody>'
    return html_content

def get_td_html(td):
    result = ""
    if td == "":
        return result
    if type(td) == type("a"):
        return '<font>%s</font>'%td
    if td[0] == "Pass":
        result += '<a onclick="show_report(this)"><span style="background-color:green"><b>Pass</b></span></a><br><font class="file_path" style="display:none;">%s</font>' % td[2]
    elif td[0] == "Failed":
        result += '<a onclick="show_report(this)"><span style="background-color:red"><b>Failed</b></span></a><br><font class="file_path" style="display:none;">%s</font>' % td[2]
    if td[1]:
        result += '<font>%s</font><br>'%td[1]
    return result

def get_version_button(td):
    return '<a onclick="click_version(this)">%s</a>' % td

def get_version_checksum_and_time2(version_path):
    f = open(version_path, 'r')
    info = f.readlines()
    info = info[0].replace("\n", "")
    if "TigerGraph version" not in info:
        return None, None, None
    info = info.split(" ")
    if info[2] >= "3.0.0":
        info = info[3:]
        count = len(info)/6
        commit_str=""
        lastest_time = "1900-01-01 00:00:00"
        gadmin_info = ""
        max_len = [0]*count
        for i in range(count):
            for j in range(6):
                if len(info[i*6+j]) > max_len[j]:
                    max_len[j] = len(info[i*6+j])
            commit_str += info[i*6+2]
            temp_time = info[i*6+3] + " " + info[i*6+4]
            if temp_time > lastest_time:
                lastest_time = temp_time
        m = hashlib.md5()
        m.update(commit_str)
        check_sum = m.hexdigest()
        for i in range(count):
            for j in range(6):
                gadmin_info += info[i*6+j] + "&nbsp;"*(max_len[j] - len(info[i*6+j])) + "&nbsp;"*2
            gadmin_info += "<br>"
        return check_sum, lastest_time, gadmin_info
    else:
        return "", "", ""

def get_version_checksum_and_time(version_path):
    f = open(version_path, 'r')
    info = f.readlines()
    info = info[0].replace("\n", "")
    if "TigerGraph version" not in info:
        return None, None, None
    info = info.split(" ")
    if info[2] >= "3.0.0":
        version = info[2]
        info = info[3:]
        count = len(info)/6
        commit_str=""
        lastest_time = "1900-01-01 00:00:00"
        gadmin_info = '<div class="ui button">%s</div><div class="ui flowing popup right center transition hidden"><div class="ui four column divided center aligned grid">'
	column_list = ['<div class="column">'] * 4
        max_len = [0]*count
        for i in range(count):
            for j in range(6):
                if len(info[i*6+j]) > max_len[j]:
                    max_len[j] = len(info[i*6+j])
            commit_str += info[i*6+2]
            temp_time = info[i*6+3] + " " + info[i*6+4]
            if temp_time > lastest_time:
                lastest_time = temp_time
        m = hashlib.md5()
        m.update(commit_str)
        check_sum = m.hexdigest()
        gadmin_info = gadmin_info % (version + "_" + check_sum[:10])
        for i in range(count):
            for j in range(6):
                if j <= 2:
                    column_list[j] += '<p>%s</p>'%info[i*6+j]
                elif j == 3:
                    column_list[3] += '<p>' + info[i*6+j] + ' '
                elif j == 4:
                    column_list[3] += info[i*6+j] + ' '
                elif j == 5:
                    column_list[3] += info[i*6+j] + '</p>'
                #gadmin_info += info[i*6+j] + "&nbsp;"*(max_len[j] - len(info[i*6+j])) + "&nbsp;"*2
        for i in range(4):
            column_list[i] += "</div>"
        gadmin_info += "".join(column_list) + "</div></div>"
            #gadmin_info += "<br>"
        return check_sum, lastest_time, gadmin_info
    else:
        return "", "", ""
