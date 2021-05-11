# coding:utf-8

import requests

QUERY_URL = "http://192.168.11.191:9000/query/mwh_graph/top_cases?days=%s&typ=%s"
PR_URL = "https://github.com/tigergraph/%s/pull/%s"
JOB_URL = "http://192.168.11.192:8080/view/MIT WIP and Hourly Pipelines/job/%s_test/%s/"
STR_LENGHT = 30

def compare_time(x, y):
	t_x = x[1].split("-")
	t_y = y[1].split("-")
	for i in range(len(t_x)):
		if int(t_x[i]) > int(t_y[i]):
			return 1
		elif int(t_x[i]) == int(t_y[i]):
			continue
		else:
			return -1
	return 0

def check_pr_exclude(case_name, pr_name):
	if case_name == "cqrs":
		if pr_name == "cqrs":
			return False
	elif case_name == "rest":
		if pr_name == "realtime":
			return False
	elif case_name == "blackbox":
		return False
	return True

def get_top_cases_html(days, typ, exclude):
	res = requests.get(QUERY_URL%(days, typ))
    	res = res.json()
	res = res.get("results")[0].get("@@result", [])
    	html = ""
    	if res:
		active = 0
        	for info in res:
			html_block = ""
			if active%2 == 0:
				html_block += '<tr class="active">'
			else:
				html_block += '<tr>'
			job_count = info['total_num']
	        	html_block += '<td rowspan="ROWS" style="vertical-align:middle;">%s</td><td rowspan="ROWS" style="vertical-align:middle;">%s</td><td rowspan="ROWS" style="vertical-align:middle;">JOB_COUNT</td>'%(info['ctype'], info['case_name'])
		        jobs = info['jobs'].split()
		        #html += '<td></td><td></td><td></td></tr>'
	        	temp = {}
	       		for job in jobs:
	        		infos = job.split(":")
		        	if infos[1] not in temp:
		        		temp[infos[1]] = [[infos[0], infos[2]]]
	        		else:
	        			temp[infos[1]].append([infos[0], infos[2]])
		        pr_info_list = []
		        for k in temp:
	        		temp[k].sort(cmp=compare_time, reverse=True)
	        		jobs_str = ""
		        	for jobs in temp[k]:
		        		jurl = JOB_URL %(jobs[0][:3],jobs[0][3:])
	        			jobs_str += '<a href="%s" target="_blank">%s</a> '%(jurl, jobs[0])
	        		pr_info_list.append([k, temp[k][0][1], jobs_str])
		       	pr_info_list.sort(cmp=compare_time, reverse=True)
			row_count = 0
                        ind = 0
		       	for pr_info in pr_info_list:
                                valid = True
                                html_temp = ""
	       			dtime = pr_info[1].split("-")
				for i in range(6):
					if i !=0 and len(dtime[i]) == 1:
						dtime[i] = "0%s"%dtime[i]
                                if ind != 0:
					if active%2 == 0:
						html_temp += '<tr class="active">'
					else:
						html_temp += "<tr>"
				ind += 1
		       		html_temp += '<td nowrap class="extra">%s-%s-%s %s:%s:%s</td>' %(dtime[0],dtime[1],dtime[2],dtime[3],dtime[4],dtime[5])
		       		prs = pr_info[0].split(";")
				str_len = 0
				html_temp += '<td class="extra">'
		       		for pr in prs:
			            	if "#" not in pr:
		        	    		continue
					str_len += len(pr)
                                        if exclude == "true":
                                        	valid = check_pr_exclude(info["case_name"], pr.split("#")[0])
                                        if not valid:
						job_count -= len(pr_info[2].split('> <'))
						ind -= 1
						break
			            	purl = PR_URL % (pr.split("#")[0], pr.split("#")[1])
	        		        html_temp += '<a href="%s" target="_blank">%s</a> '%(purl, pr)
				html_temp += "</td>"
	             	        html_temp += '<td class="extra">' + pr_info[2] + "</td></tr>"
				if valid:
					html_block += html_temp
					row_count += 1
			active += 1
			if row_count != 0:
	                        html_block = html_block.replace("ROWS", str(row_count))
				html_block = html_block.replace("JOB_COUNT", str(job_count))
				html += html_block
		        #html += "</td></table></tr>"
	return html
