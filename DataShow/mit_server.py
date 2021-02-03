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


def get_top_cases_html(days, typ):
	res = requests.get(QUERY_URL%(days, typ))
    	res = res.json()
	res = res.get("results")[0].get("@@result", [])
    	html = ""
    	if res:
		active = 0
        	for info in res:
			if active%2 == 0:
				html += '<tr class="active">'
			else:
				html += '<tr>'
	        	html += '<td rowspan="ROWS" style="vertical-align:middle;">%s</td><td rowspan="ROWS" style="vertical-align:middle;">%s</td><td rowspan="ROWS" style="vertical-align:middle;">%s</td>'%(info['ctype'], info['case_name'], info['total_num'])
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
                        html = html.replace("ROWS", str(len(pr_info_list)))
                        ind = 0
		       	for pr_info in pr_info_list:
	       			dtime = pr_info[1].split("-")
				for i in range(6):
					if i !=0 and len(dtime[i]) == 1:
						dtime[i] = "0%s"%dtime[i]
                                if ind != 0:
					if active%2 == 0:
						html += '<tr class="active">'
					else:
						html += "<tr>"
				ind += 1
		       		html += "<td nowrap>%s-%s-%s %s:%s:%s</td>" %(dtime[0],dtime[1],dtime[2],dtime[3],dtime[4],dtime[5])
		       		prs = pr_info[0].split(";")
				str_len = 0
				html += "<td>"
		       		for pr in prs:
			            	if "#" not in pr:
		        	    		continue
					str_len += len(pr)
			            	purl = PR_URL % (pr.split("#")[0], pr.split("#")[1])
	        		        html += '<a href="%s" target="_blank">%s</a> '%(purl, pr)
				html += "</td>"
	             	        html += "<td>" + pr_info[2] + "</td></tr>"
			active += 1
		        #html += "</td></table></tr>"
	return html
