# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 03:03:14 2018

@author: Dennis
"""

import pandas as pd
import os
import csv
import re
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import urllib

#######################



##########SUB##########

def getdatadatelist (symbol = "AAPL"): #uses stock full charts to create trading days list
	fychart = requests.get('https://api.iextrading.com/1.0/stock/'+symbol+'/chart/5y')
	json_data = json.loads(fychart.text)
	df = pd.DataFrame(json_data)
	datelist = list(df['date'])
	datelist = [i.replace('-','') for i in datelist]
	return datelist

def getsymlist ():
	allsymlist = requests.get('https://api.iextrading.com/1.0/ref-data/symbols')
	symlistjson = json.loads(allsymlist.text)
	symdf = pd.DataFrame(symlistjson)
	#symdf = symdf.set_index('symbol')
	symlist = list(symdf['symbol'])
	return symlist

def url2df (url='https://api.iextrading.com/1.0/ref-data/symbols'):
	r = requests.get(url)
	json_data = json.loads(r.text)
	#df = pd.DataFrame(json_data)
	try:
		df = pd.DataFrame(json_data)
	except ValueError:
		df = pd.DataFrame(data=json_data, index=[json_data['symbol']] )
	return df

def savetofile (symlist, datatype, savelocation="RawFiles"):
	for i in symlist:
		url = 'https://api.iextrading.com/1.0/stock/'+i+'/company'
		filename = 'Company.'+i+'.JSON'
		filename = filename.replace("*",'')
		print('fetching ' + i + ' via https://api.iextrading.com/1.0/stock/'+i+'/company')
		try:
			urllib.request.urlretrieve(url, savelocation+'\\Company\\'+filename)
		except OSError:
			print('Fetch '+url+' failed to save to '+filename)
			

def findstartdate_sub (datelist, testurl='https://api.iextrading.com/1.0/stock/aapl/chart/date/'): #list must be sorted
	#print('findstartdatecalled' + ' '.join(datelist))
	if len(datelist) <= 2:
		for i in range(len(datelist)):
			url = testurl+datelist[i]
			if testresponse(url):
				#print('url is ' + url)
				break
		return datelist[i]
	else: 
		testindex = int(len(datelist)/2)
		url = testurl+datelist[testindex]
		#print('testindex ' + str(testindex))
		if testresponse(url):
			return findstartdate(datelist[:testindex+1], testurl)
		else:
			return findstartdate(datelist[testindex:], testurl)


def findstartdate (datelist, testurl='https://api.iextrading.com/1.0/stock/aapl/chart/date/'): #wrapper to sort list
	datelist.sort()
	urle = testurl+datelist[-1]
	if testresponse(urle):
		return findstartdate_sub(datelist)
	else:
		return 0
		
	
def testresponse (url):
	r = requests.get(url)
	#print(url)
	json_data = json.loads(r.text)
	if (json_data):
		return 1
	else:
		return 0
	
   
#######################	

print("Begin \n")

loge = open('RawFiles\\Company\\.errorlog.txt','w')
logd = open('RawFiles\\Company\\.downloadlog.txt','w')

#r = requests.get('https://api.iextrading.com/1.0/stock/market/collection/sector?collectionName=Technology')
#json_data = json.loads(r.text)
#json_data = json_data['data']
#df = pd.DataFrame(json_data)
#df = df.set_index('symbol')
#print(df.loc['AAPL'])
#full = pd.DataFrame()

datelist = getdatadatelist()
firstdate = findstartdate(datelist)
firstdateindex = datelist
firstdateindex.sort()
firstdateindex = firstdateindex.index(firstdate)
#datelist.reverse()

symlist = getsymlist()
#symlist=['PRN','SERV#']
for i in symlist:
	url = 'https://api.iextrading.com/1.0/stock/'+i+'/company'
	filename = 'Company.'+i+'.JSON'
	filename = filename.replace("*",'')
	print('fetching ' + i + ' via https://api.iextrading.com/1.0/stock/'+i+'/company')
	try:
		urllib.request.urlretrieve(url, 'RawFiles\\Company\\'+filename)
		logd.write('Fetch '+url+' sucessfully saved to '+filename+'\n')
	except OSError:
		print('Fetch '+url+' failed to save to '+filename)
		loge.write('Fetch '+url+' failed to save to '+filename+'\n')
		#pass
	#r = requests.get('https://api.iextrading.com/1.0/stock/'+i+'/company')
	#json_data = json.loads(r.text)
	#df2 = pd.DataFrame(json_data)
	#frames = [full, df2]
	#full = pd.concat(frames)
	#if i == "AAPL":
	#	break
	
logd.close()
loge.close()


"""
exit()

r = requests.get('https://api.iextrading.com/1.0/stock/aapl/company')
json_data = json.loads(r.text)
#json_data = json_data['data']

df2 = pd.DataFrame(json_data)


#keys = list(json_data[0].keys)

size = len(json_data)
print(size)

for i in range(len(json_data)):
	
	#if not json_data[i]['close']:
	if not 'close' in json_data[i]:
		json_data[i]['close']=json_data[i-1]['close'] #trail data if missing
	print (json_data[i]['date']," = ",json_data[i]['close'])
	



closeprices = [json_data[i]['close'] for i in range(len(json_data))]
timestamps = [json_data[i]['date'] for i in range(len(json_data))]

a = range(len(json_data)) 
#np.linspace(0,np.amax(closeprices),1000)
plt.plot(a,closeprices)

"""