# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 22:46:58 2018

@author: Dennis
"""

import pandas as pd
#import os
#import csv
#import re
#import numpy as np
#import matplotlib.pyplot as plt
import requests
import json
#import urllib
#import urllib.reqests
#import urllib.error
import time

##########GLOBALS##############################################################

requesttimeout = 10
defaultrawdir = "RawFiles"

##########SUB##################################################################

def getdatadatelist (symbol = "AAPL"): #uses stock full charts to create trading days list
	try:
		fychart = requests.get("https://api.iextrading.com/1.0/stock/"+symbol+"/chart/5y",timeout=requesttimeout)
	except:
		print("Failed to fetch "+symbol+" 5Y Chart")
		return 0
	json_data = json.loads(fychart.text)
	df = pd.DataFrame(json_data)
	datelist = list(df["date"])
	datelist = [i.replace("-","") for i in datelist]
	return datelist

def getsymlist ():
	try:
		allsymlist = requests.get("https://api.iextrading.com/1.0/ref-data/symbols",timeout=requesttimeout)
	except:
		print("Failed to fetch symbols list")
		return 0
	symlistjson = json.loads(allsymlist.text)
	symdf = pd.DataFrame(symlistjson)
	#symdf = symdf.set_index("symbol")
	symlist = list(symdf["symbol"])
	return symlist

def dfrequest (datatype, symbol, date="0", local=0, localdir=defaultrawdir):
	if local:
		filename = datatype+'.'+symbol
		filename = filename.replace('*','9')
		filename = filename.replace('#','9')
				
		if len(date)==8:
			filename = filename+'.'+date
		filename = filename+".JSON"
		fileloc = localdir+"\\"+datatype+"\\"
		file = fileloc+filename
		jsonfile = open(file, "r", encoding="UTF-8")
		json_data = json.loads(jsonfile.read())
		jsonfile.close()
		df = pd.DataFrame(json_data)
		return df		
	else:
		url = urlsyntax(datatype, symbol, date)
		return url2df(url)

def url2df (url="https://api.iextrading.com/1.0/ref-data/symbols"):
	try:
		r = requests.get(url,timeout=requesttimeout)
	except:
		print("Failed to fetch "+url)
		return 0
	json_data = json.loads(r.text)
	#df = pd.DataFrame(json_data)
	try:
		df = pd.DataFrame(json_data)
	except ValueError:
		df = pd.DataFrame(data=json_data, index=[json_data["symbol"]] )
	return df

def findstartdate_sub (datelist, testurl="https://api.iextrading.com/1.0/stock/aapl/chart/date/"): #list must be sorted
	#print("findstartdatecalled" + " ".join(datelist))
	if len(datelist) <= 2:
		for i in range(len(datelist)):
			url = testurl+datelist[i]
			if testresponse(url):
				#print("url is " + url)
				break
		return datelist[i]
	else: 
		testindex = int(len(datelist)/2)
		url = testurl+datelist[testindex]
		#print("testindex " + str(testindex))
		if testresponse(url):
			return findstartdate(datelist[:testindex+1], testurl)
		else:
			return findstartdate(datelist[testindex:], testurl)


def findstartdate (datelist, testurl="https://api.iextrading.com/1.0/stock/aapl/chart/date/"): #wrapper to sort list
	datelist.sort()
	urle = testurl+datelist[-1]
	if testresponse(urle):
		return findstartdate_sub(datelist)
	else:
		return 0
		
	
def testresponse (url):
	try:
		r = requests.get(url,timeout=requesttimeout)
	except:
		print("Failed to recieve any response")
		return 0
	#print(url)
	json_data = json.loads(r.text)
	if (json_data):
		return 1
	else:
		return 0
	
def download_file(url,fileloc,to=requesttimeout,redirect=True):
	try:
		r = requests.get(url, allow_redirects=redirect, timeout=to)
		with open(fileloc, 'wb') as f:
			f.write(r.content)
		del r
		return 1
	except:
		return 0
	
		
	
###############################################################################

def dumptofile (symlist, datatype, savelocation=defaultrawdir, datelist='1', overwrite=0):
	
	t1=time.gmtime()
	tt1=time.time()
	
	begintime = time.strftime('%a, %d %b %Y %H:%M:%S GMT',t1)
	
	datatype = datatype.capitalize()
	
	print("Begin IEX "+datatype+" DB Dump at "+begintime)
	
	fileloc = savelocation+"\\"+datatype+"\\"
	
	logd = open(fileloc+".downloadlog.txt","a+")
	loge = open(fileloc+".errorlog.txt","a+")

	logd.write("\n##############################################################################################################\n")
	loge.write("\n##############################################################################################################\n")
	
	logd.write(begintime+ "\nBegin Logging:\n")
	loge.write(begintime+ "\nBegin Logging:\n")
	
	for sym in symlist:
		for date in datelist:
			url = urlsyntax(datatype,sym,date)
			filename = datatype+'.'+sym
			filename = filename.replace('*','9')
			filename = filename.replace('#','9')
			
			
			if len(date)==8:
				filename = filename+'.'+date
			filename = filename+".JSON"
			
			file = fileloc+filename
			
			print("Fetching " + sym + " via " + url + " try saving to "+file)
			
			if (not overwrite):
				
				try:
					testfile = open(file, "r", encoding="UTF-8")
					test_json = json.loads(testfile.read())
					testfile.close()
					if (test_json):
						print(file+" Already exist skipping..")
						continue
				except FileNotFoundError:
					print(file+" File not found downloading..")
				except ValueError:
					print(file+" Bad JSON found downloading..")
					
			if(download_file(url, file)):
				print("Fetch "+url+" sucessfully saved to "+file)				
				logd.write("Fetch "+url+" sucessfully saved to "+file+"\n")
			else:
				print("Fetch "+url+" failed to save to "+file)
				loge.write("Fetch "+url+" failed to save to "+file+"\n")
				
	t2 = time.gmtime()
	tt2 = time.time()
	
	endtime = time.strftime('%a, %d %b %Y %H:%M:%S GMT',t2)	 
	
	elapsedtime = str(tt2-tt1)
	
	logd.write(endtime+ "\nEnd Logging Time Elapsed: \n"+elapsedtime)
	loge.write(endtime+ "\nEnd Logging Time Elapsed: \n"+elapsedtime)
	
	
	logd.close()
	loge.close()
	
	print("End IEX "+datatype+" DB Dump at "+endtime+ " Took :"+elapsedtime+" seconds. \n")
	
	return 1;



def urlsyntax (datatype, symbol="AAPL", date="n/a"):
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
			'Chart1d':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/1d",
			'Chartdate':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/date/"+date,
			'Chartdynamic':"https://api.iextrading.com/1.0/stock/"+symbol+"/chart/dynamic",
			
			'Dividends5y':"https://api.iextrading.com/1.0/stock/"+symbol+"/dividends/5y",
			'Dividends2y':"https://api.iextrading.com/1.0/stock/"+symbol+"/dividends/2y",
			'Dividends1y':"https://api.iextrading.com/1.0/stock/"+symbol+"/dividends/1y",
			'Dividendsytd':"https://api.iextrading.com/1.0/stock/"+symbol+"/dividends/ytd",
			'Dividends6m':"https://api.iextrading.com/1.0/stock/"+symbol+"/dividends/6m",
			'Dividends3m':"https://api.iextrading.com/1.0/stock/"+symbol+"/dividends/3m",
			'Dividends1m':"https://api.iextrading.com/1.0/stock/"+symbol+"/dividends/1m",
			
			'Splits5y':"https://api.iextrading.com/1.0/stock/"+symbol+"/splits/5y",
			'Splits2y':"https://api.iextrading.com/1.0/stock/"+symbol+"/splits/2y",
			'Splits1y':"https://api.iextrading.com/1.0/stock/"+symbol+"/splits/1y",
			'Splitsytd':"https://api.iextrading.com/1.0/stock/"+symbol+"/splits/ytd",
			'Splits6m':"https://api.iextrading.com/1.0/stock/"+symbol+"/splits/6m",
			'Splits3m':"https://api.iextrading.com/1.0/stock/"+symbol+"/splits/3m",
			'Splits1m':"https://api.iextrading.com/1.0/stock/"+symbol+"/splits/1m",
			
			'Corpact':"https://api.iextrading.com/1.0/ref-data/daily-list/corporate-actions",
			'Corpactdate':"https://api.iextrading.com/1.0/ref-data/daily-list/corporate-actions/"+date,

			'Earnings':"https://api.iextrading.com/1.0/stock/"+symbol+"/earnings",
			
			'Effspread':"https://api.iextrading.com/1.0/stock/"+symbol+"/effective-spread",
			
			'Financials':"https://api.iextrading.com/1.0/stock/"+symbol+"/financials",
			'Financialsannual':"https://api.iextrading.com/1.0/stock/"+symbol+"/financials?period=annual",
			
			'Keystats':"https://api.iextrading.com/1.0/stock/"+symbol+"/stats",
			
			
			}
	return syntax[datatype] if datatype in syntax else 0


###############################################################################
