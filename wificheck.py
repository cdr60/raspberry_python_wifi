#!/usr/bin/python3
import sys
import os
import functools
import time

def get_name(cell):
	return matching_line(cell,"ESSID:")[1:-1]

def get_quality(cell):
	quality = matching_line(cell,"Quality=").split()[0].split('/')
	return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3) + " %"

def get_channel(cell):
	return matching_line(cell,"Channel:")

def get_encryption(cell):
	enc=""
	if matching_line(cell,"Encryption key:") == "off":
		enc="Open"
	else:
		for line in cell:
			matching = match(line,"IE:")
			if matching!=None:
				wpa=match(matching,"WPA Version ")
				if wpa!=None:
					enc="WPA v."+wpa
		if enc=="":
			enc="WEP"
	return enc

def get_address(cell):
	return matching_line(cell,"Address: ")

# Here's a dictionary of rules that will be applied to the description of each
# cell. The key will be the name of the column in the table. The value is a
# function defined above.

rules={"Name":get_name,
	   "Quality":get_quality,
	   "Channel":get_channel,
	   "Encryption":get_encryption,
	   "Address":get_address,
	   }

# Here you can choose the way of sorting the table. sortby should be a key of
# the dictionary rules.

def sort_cells(cells):
	sortby = "Quality"
	reverse = True
	#cells.sort(None, lambda el:el[sortby], reverse)
	sorted(cells,key=lambda el:el[sortby],reverse=reverse)

# You can choose which columns to display here, and most importantly in what order. Of
# course, they must exist as keys in the dict rules.

columns=["Name","Address","Quality","Channel","Encryption"]




# Below here goes the boring stuff. You shouldn't have to edit anything below
# this point

def matching_line(lines, keyword):
	"""Returns the first matching line in a list of lines. See match()"""
	for line in lines:
		matching=match(line,keyword)
		if matching!=None:
			return matching
	return None

def match(line,keyword):
	"""If the first part of line (modulo blanks) matches keyword,
	returns the end of that line. Otherwise returns None"""
	line=line.lstrip()
	length=len(keyword)
	if line[:length] == keyword:
		return line[length:]
	else:
		return None

def parse_cell(cell):
	"""Applies the rules to the bunch of text describing a cell and returns the
	corresponding dictionary"""
	parsed_cell={}
	for key in rules:
		rule=rules[key]
		parsed_cell.update({key:rule(cell)})
	return parsed_cell

def print_table(table):
	widths=map(max,map(lambda l:map(len,l),zip(*table))) #functional magic

	justified_table = []
	for line in table:
		justified_line=[]
		for i,el in enumerate(line):
			justified_line.append(el.ljust(widths[i]+2))
		justified_table.append(justified_line)
	
	for line in justified_table:
		for el in line:
			print (el)

#affichage normal
def print_cells(cells=0):
	table=[columns]
	for cell in cells:
		cell_properties=[]
		for column in columns:
			cell_properties.append(cell[column])
		table.append(cell_properties)
	print_table(table)

#minquality = qualite minimal pour etre retenue
def filter_cells(cells,minquality=0,mywifihotspot=[]):
	result=[]
	for cell in cells:
		#recuperer la valeur de la qualite
		q=cell["Quality"]
		iq=q.split("%")
		if len(iq)>0: valq=iq[0].strip()
		else: valq="0"
		
		#recupere le nom du SSID
		nssid=cell["Name"]
		#print(str(valq)+" "+nssid+" "+str(minquality))
		if ((int(valq)>=minquality) and (nssid in mywifihotspot)) or (len(mywifihotspot)==0):
			#print(nssid)
			result.append(cell)
	return result
	
	
#scan des wifi dispo
def ScanWifiHotSpot(interface="wlan0",minquality=10):
	result=[]
	cells=[[]]
	parsed_cells=[]
	myCmd = os.popen('iwlist '+interface+' scan').read()
	CmdLine=myCmd.split("\n")
	for line in CmdLine:
		cell_line = match(line,"Cell ")
		if cell_line != None:
			cells.append([])
			line = cell_line[-27:]
		cells[-1].append(line.rstrip())
	cells=cells[1:]
	for cell in cells:
		parsed_cells.append(parse_cell(cell))
	for cell in parsed_cells:
		try:
			q=cell["Quality"].split("%")
			if (len(q)>0): q=int(q[0])
		except:
			q=0
		if (q>=minquality): result.append(cell["Name"])
	return result

#scan des wifi dispo, tri par signal decroissant, filtre sur ceux dont le signal est suffisant et parmis une list de hotspot
#choix du meilleur parmis ceux qui restent
def ChooseWifiHotSpot(interface="wlan0",minquality=10,mywifihotspot=['SFR_68B8','AndroiAP']):
	result=""
	cells=[[]]
	parsed_cells=[]
	myCmd = os.popen('iwlist '+interface+' scan').read()
	CmdLine=myCmd.split("\n")
	

	for line in CmdLine:
		cell_line = match(line,"Cell ")
		if cell_line != None:
			cells.append([])
			line = cell_line[-27:]
		cells[-1].append(line.rstrip())

	cells=cells[1:]

	for cell in cells:
		parsed_cells.append(parse_cell(cell))

	sort_cells(parsed_cells)
	print(parsed_cells)
	parsed_cells=filter_cells(parsed_cells,minquality,mywifihotspot)
	#print(parsed_cells)
	if (len(parsed_cells)>0):
		result=parsed_cells[0]["Name"]
	return result
	
#connexion à 1 hotspot
def ConnectWifi(country="FR",interface="wlan0",ssid='',passw=''):
	result=""
	conffilename="/etc/wpa_supplicant/wpa_supplicant.conf"
	if (os.path.exists(conffilename)==True): os.remove(conffilename)
	
	f=open(conffilename,"w")
	f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
	f.write("update_config=1\n")
	f.write("country=FR\n")
	f.close()
	
	cmd="sudo chmod a+w "+conffilename
	#print(cmd)
	myCmd = os.popen(cmd).read()
	CmdLine=myCmd.split("\n")
	
	cmd="wpa_passphrase "+ssid+" "+passw+" >> "+conffilename
	#print(cmd)
	myCmd = os.popen(cmd).read()
	CmdLine=myCmd.split("\n")
	
	cmd="wpa_cli -i "+interface+" reconfigure"
	#print(cmd)
	myCmd = os.popen(cmd).read()
	CmdLine=myCmd.split("\n")
	
	time.sleep(1)
	
	i=0
	completed=""
	cmd="wpa_cli -i "+interface+" status | grep wpa_state | cut -d= -f2"
	#print(cmd)
	while (i<10) and (completed!="COMPLETED"):
		myCmd = os.popen(cmd).read()
		CmdLine=myCmd.split("\n")
		if len(CmdLine)>1: completed=CmdLine[0]
		print(completed+".....")
		if (completed!="COMPLETED"):
			i=i+1
			time.sleep(5)
	if (completed!="COMPLETED"): return result
	
	i=0
	cmd="wpa_cli -i "+interface+" status | grep ip_address | cut -d= -f2"
	#print(cmd)
	while (i<10) and (result==""):
		myCmd = os.popen(cmd).read()
		CmdLine=myCmd.split("\n")
		if len(CmdLine)>1:
			ip=CmdLine[0].split(".")
			if (len(ip)==4):
				result=CmdLine[0]
		if result=="":
			i=i+1
			time.sleep(2)
	return result
	
if __name__ == "__main__":
#	BESTWIFI=ChooseWifiHotSpot("wlan0",10,mywifihotspot=['SFR_68B8','MAISON','acpnwifi2'])
#	print("BESTWIFI : "+BESTWIFI)

#	r=ConnectWifi("FR","wlan0","piwifi4","jiqva74e")
#	print(r)

	r=ScanWifiHotSpot()
	print(r)
