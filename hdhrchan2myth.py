#!/usr/bin/env python3

import sys, json, urllib3, subprocess, os

def removeNonAscii(s):
	s = s.replace("&", "and")
	return "".join([x if ord(x) < 128 else '_' for x in s])

if __name__== "__main__":
	print('Detecting HDHomeRun device')
	try:
		http = urllib3.PoolManager()
		discover_url_response = http.request('GET',"http://my.hdhomerun.com/discover")
		data = discover_url_response.data
		hdhrDevice = json.loads(data)
	except:
		print("Aborting (no HdHomeRun device detected)")
		sys.exit(0)
	if 'DeviceID' in hdhrDevice[0]:
		print("Detected HDHomeRun device at " + hdhrDevice[0]["LocalIP"])
		device_auth_response = http.request('GET',hdhrDevice[0]["LineupURL"])
		data = device_auth_response.data
		Lineup_raw = json.loads(data)
		Lineup = removeNonAscii(Lineup_raw)
		if (len(Lineup) > 0):
			print("Copying channels from HDHomeRun device")
			with open('/tmp/xmltv.xml', 'w') as xml_file:
				xml_file.write('<?xml version="1.0" encoding="ISO-8859-1"?>'+'\n')
				xml_file.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">'+'\n')
				xml_file.write('\n')
				xml_file.write('<tv source-info-name="HDHR" generator-info-name="hdhrchan2myth.py">'+'\n')
				for i in range(len(Lineup)):
					xml_file.write(' <channel id="'+Lineup[i]['GuideNumber']+'">'+'\n')
					xml_file.write('  <display-name>'+Lineup[i]['GuideNumber']+' '+Lineup[i]['GuideName']+'</display-name>'+'\n')
					xml_file.write('  <display-name>'+Lineup[i]['GuideName']+'</display-name>'+'\n')
					xml_file.write('  <display-name>'+Lineup[i]['GuideNumber']+'</display-name>'+'\n')
					xml_file.write(' </channel>'+'\n')
				xml_file.write('</tv>')
		else:
			print("Aborting (no lineup for device found)")
			sys.exit(0)
	else:
		print("Aborting (no usable HdHomeRun device detected)")
		sys.exit(0)
	print("Adding channels to MythTV")
	subprocess.call('mythfilldatabase --quiet --refresh 1 --file --sourceid 1 --xmlfile /tmp/xmltv.xml', shell=True)
