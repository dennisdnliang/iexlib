# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import os
import csv
import re
import numpy as np

import matplotlib.pyplot as plt

import requests
import json

print("Hello world! \n");

module = "MSCI"
symbol = "ACWI.R"
item = "PI$"
date = "20180726"
chgopt = "CHG-1D"

output = os.system("autoserve.plx " + module + "," + symbol + "," + item + "," + date + "," + chgopt)

print (("autoserve.plx " + module + "," + symbol + "," + item + "," + date + "," + chgopt))

a = np.linspace(0, 10, 100)
b = np.exp(-a)
plt.plot(a,b)
plt.show()

r = requests.get('https://api.iextrading.com/1.0/stock/qqq/chart/5y')
r = requests.get('https://api.iextrading.com/1.0/stock/eri/chart/dynamic')

json_data = json.loads(r.text)
json_data = json_data['data']
print(json_data[0]['marketClose'])

#keys = list(json_data[0].keys)

size = len(json_data)
print(size)

for i in range(len(json_data)):
	"""
	if 'marketClose' in json_data[i] and 'close' in json_data[i]:
		diff = json_data[i]['marketClose']-json_data[i]['close']  
		
		print (json_data[i]['minute'],"\n marketClose = ",json_data[i]['marketClose'],"\n close = ",json_data[i]['close'])
		print ("diff = ",diff)
		
		#print (json_data[i-1]['minute'],"\n marketClose = ",json_data[i-1]['marketClose'],"\n close = ",json_data[i-1]['close'])

		
		print ("\n\n")
	"""
	#if not json_data[i]['marketClose']:
	if not 'marketClose' in json_data[i]:
		print ("data missing for ",json_data[i-1]['minute'])
		
		if 'close' in json_data[i]:
			json_data[i]['marketClose']=json_data[i]['close']		
		else:
			json_data[i]['marketClose']=json_data[i-1]['marketClose'] #trail data if missing
	
	



closeprices = [json_data[i]['marketClose'] for i in range(len(json_data))]
timestamps = [json_data[i]['minute'] for i in range(len(json_data))]

a = range(len(json_data)) 
#np.linspace(0,np.amax(closeprices),1000)
plt.plot(a,closeprices)

