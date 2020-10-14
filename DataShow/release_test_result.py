# coding:utf-8

import re
import os

MODULE_HEADS = [
    "install",
    "schema_change",
    "backup",
    "restore",
    "secondary_index",
    "service_failure",
    "update_test",
    "service_recover",
    "gsql_stress",
    "wcc_pagerank",
    "gse_compaction_enable",
    "query_installation",
    "concurrent_load",
    "stress_test",
    "upgrade",
    "clear_graph_store",
    "database_export",
    "database_import",
    "kafka_load",
    "ldap",
    "tpch_queries",
    "gse_compaction_disable",
    "ldbc_queries",
    "ssl_config",
    "token_config",
    "cross_region_replication",
    "create_schema",
    "load_data",
    "batch_query",
    "hub_load",
    "deletion",
    "tpch_load",
]

# RESULT_DIR="E:/work/release_test_result"
RESULT_DIR="/home/graphsql/release_test_result"

def get_module_name(file_name, file_path):
    if os.path.isfile(file_path):
        if file_name.startswith("install_") and file_name.endswith("_result"):
            return "install"
        elif file_name.endswith("_result"):
            prefix = file_name.replace("_result", "")
            if prefix in ["schema_change","backup","restore","update","query_installation","concurrent_load","upgrade","clear_graph_store","database_export","database_import","kafka_load","ldap","ssl_config","create_schema","load_data","deletion"]:
                return prefix
            elif prefix == "index":
                return "secondary_index"
            elif prefix == "token_enable":
                return "token_config"
            elif prefix == "CRR_config":
                return "cross_region_replication"
        elif file_name.startswith("wcc_pagerank_"):
            return "wcc_pagerank"
        elif file_name.startswith("gse_compaction_enable"):
            return "gse_compaction_enable"
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
    # 0: pass or failed or blank : string
    # 1: simple result : string'
    # 2: result file path : string
    if module_name == "install":
        r_str = "Failed"
        s_result = ""
        for line in data:
            if "Installation Finished" in line:
                r_str = "Pass"
            if "installation finished" in line:
                s_result = line
        return [r_str, s_result, file_path.replace("\\","/").replace("/","//")]
    return ["", "", ""]

def get_release_result():
    # return "<tr>"+"<td>pass</td>"*(len(MODULE_HEADS)+1)+"</tr>"
    dirs = os.listdir(RESULT_DIR)
    # {version: {tag_job_id :{module_name:["Pass","cost time:188s","e:/hdhdhdh"]}}}
    result = {}
    for dir in dirs:
        dir_path = os.path.join(RESULT_DIR, dir)
        if not os.path.isdir(dir_path):
            continue
        version = re.match('.*(\d\.\d\.\d).*', dir)
        if not version or version.group(1) <= '2.2.0':
            continue
        version = version.group(1)
        if version not in result:
            result[version] = {}
        test_plan = dir.split('_release')[0]
        time = re.match('.*(\d\d-\d\d-\d\d\d\d).*', dir)
        time = time.group(1)
        job_id = dir.split('_')[-1]
        index = "%s_%s"%(time, job_id)
        if index not in result[version]:
            result[version][index] = {}

        files = os.listdir(dir_path)
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
        index_list = result[ver].keys()
        index_list.sort(reverse=True)
        html_tag_tbody = []
        for ind in index_list:
            html_tag_tr = [""] * (len(MODULE_HEADS)+1)
            html_tag_tr[0] = ver+"_"+ind.split("_")[0]
            module_info = result[ver][ind]
            for i in range(len(MODULE_HEADS)):
                mod = MODULE_HEADS[i]
                if mod in module_info:
                    html_tag_tr[i+1] = module_info[mod]
                    if html_ver_tr[i+1] == "":
                        html_ver_tr[i+1] = module_info[mod]
            html_tag_tbody.append(html_tag_tr)

        html_content += "<tr>"
        for i in range(len(html_ver_tr)):
            td = html_ver_tr[i]
            if i == 0:
                html_content += '<td bgcolor="#CDCD00">%s</td>'%get_version_button(td)
            else:
                html_content += '<td bgcolor="#CDCD00">%s</td>'%get_td_html(td)
        html_content += "</tr>"

        html_content += '<tbody class="childrens">'
        for info in html_tag_tbody:
            html_content += "<tr>"
            for td in info:
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
        result += '<b><font style="color:green">%s</font></b><br>'%td[0]
    elif td[0] == "Failed":
        result += '<b><font style="color:red">%s</font></b><br>'%td[0]
    if td[1]:
        result += '<font>%s</font>'%td[1]
    if td[2]:
        result += '<a onclick="show_report(this)"><b>report</b></a><br><font class="file_path" style="display:none;">%s</font>' % td[2]
    return result

def get_version_button(td):
    return '<a onclick="click_version(this)">%s</a>' % td
