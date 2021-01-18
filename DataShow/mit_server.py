# coding:utf-8

import request

QUERY_URL = "http://192.168.99.225:9000/query/mwh_graph/top_cases?days=%s&typ=%s"
PR_URL = "https://github.com/tigergraph/%s/pull/%s"

def get_top_cases(days, typ):
	res = request.get(QUERY_URL%(days, typ))
	res = res.get("result", {}).get("@@result", [])
	html = ""
	if not res:
		for info in res:
			html += "<tr><td>%s</td><td>%s</td><td>%s</td>"%(info['ctype'], info['case_name'], info['total_num'])
			jobs = info['jobs'].split()
			html += "<td>"
			for job in jobs:
				if not job:
					continue
				job_id = job.split(":")[0]
				prs = job.split(":")[1].split(";")
				for pr in prs:
					if "#" not in pr:
						continue
					purl = PR_URL % (pr.split("#")[0], pr.split("#")[1])
					html += '<a href="%s">%s</a> '%(purl, pr)
				html += "\n"
			
			html += "</td></tr>"
	return html
