#!/usr/bin/env python
import os, sys, time
import xml.etree.ElementTree as ET
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup


xmlPath = '/home/opsmon/scripts/bmc-selfmonitoring/health/'
xmlFile = 'tsps_dr_status.xml'
servers = [['ocvlp-bmc004', 'https://ocvlp-bmc004.prod.oami.eu:8043'], ['orvlp-bmc404', 'https://orvlp-bmc404.prod.oami.eu:8043']]

root = ET.Element('tsps_dr_status')
comment = ET.Comment('This XML is generated by a script called tsps_dr_check.py at ocvlp-bmc014. In case of malfunction or further changes check the script there.')
root.insert(1, comment)
root.set('time', str(time.time()))

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
for server in servers:
	try:
		page = requests.get(server[1], verify=False)
	except Exception as e: 
		print ("An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args))
		page = ''
		continue

	soup = BeautifulSoup(page.text, 'html.parser')
	if soup.find('div', attrs={'class': 'd-login'}) is not None:
		server.append ('active')
	else:
		text = 'unknown'
		results = soup.findAll('p')
		for line in results:
			if str(line).find('standby'):
				text = 'standby'
				break		
		server.append (text)	
	server.append (page.status_code)

server_aa = servers[0]
server_buc = servers[1]
# Added info into the XML
alert = ET.SubElement(root, 'server')
ET.SubElement(alert, 'name').text = server_buc[0]
ET.SubElement(alert, 'role').text = server_buc[2]
ET.SubElement(alert, 'response_code').text = str(server_buc[3])
if (server_aa[2] == 'active') or \
	(server_aa[3] != 200 and server_buc[2] == 'active'):
	ET.SubElement(alert, 'status').text = 'OK'
else:
	ET.SubElement(alert, 'status').text = 'NotOk'
dataAlarm =  ET.tostring(root).decode("utf-8")
with open(xmlPath +  xmlFile, 'w') as f:
	f.write(dataAlarm)
