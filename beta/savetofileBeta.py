# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 13:13:13 2018

@author: Dennis
"""

import requests
import urllib

def dumptofile (symlist, datatype, savelocation="RawFiles\\test", datelist='1'):

	print("Begin IEX DB Dump\n")
	
	datatype = datatype.capitalize()
	
	fileloc = savelocation+"\\"+datatype+"\\"
	
	loge = open(fileloc+".errorlog.txt","w")
	logd = open(fileloc+".downloadlog.txt","w")
	
	for i in symlist:
		for d in datelist:
			url = urlsyntax(datatype,i,d)
			filename = i+".JSON"
			filename = filename.replace('*','')
			
			if len(d)==6:
				filename = i+"."+d+".JSON"
			
			print("fetching " + i + " via " + url)
			try:
				urllib.request.urlretrieve(url, fileloc+filename)
				logd.write("Fetch "+url+" sucessfully saved to "+fileloc+filename+"\n")
			except OSError:
				print("Fetch "+url+" failed to save to "+fileloc+filename)
				loge.write("Fetch "+url+" failed to save to "+fileloc+filename+"\n")
				
		
	logd.close()
	loge.close()
	return 1;



def urlsyntax (datatype, symbol, date="n/a"):
	syntax = {
			'Company':"https://api.iextrading.com/1.0/stock/"+symbol+"/company",
			
			'Chart':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart",
			'Chart5y':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/5y",
			'Chart2y':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/2y",
			'Chart1y':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/1y",
			'Chartytd':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/ytd",
			'Chart6m':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/6m",
			'Chart3m':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/3m",
			'Chart1m':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/1m",
			'Chart1d':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart1d",
			'Chartdate':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/date/"+date,
			'Chartdynamic':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/dynamic",
			}
	return syntax[datatype] if datatype in syntax else 0

symlist = ["FB","AAPL","AMZN","NFLX","GOOGL"]
datatype = "Company"

savelocation = "RawFiles\\test\\"	